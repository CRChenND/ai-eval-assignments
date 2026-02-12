import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from pipeline_utils import BASE_DIR


def mean(values):
    return sum(values) / len(values) if values else 0.0


def stdev(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze hallucination metrics by strategy.")
    parser.add_argument(
        "--fact-check",
        default=str(BASE_DIR / "results" / "fact_check" / "fact_check.json"),
        help="Fact-check JSON path",
    )
    parser.add_argument(
        "--output",
        default=str(BASE_DIR / "results" / "analysis" / "metrics.json"),
        help="Metrics output JSON path",
    )
    args = parser.parse_args()

    fc = json.loads(Path(args.fact_check).read_text(encoding="utf-8"))["fact_checks"]

    by_strategy = defaultdict(list)
    for row in fc:
        by_strategy[row["strategy"]].append(row)

    metrics = {}
    for strategy, rows in by_strategy.items():
        known = [r for r in rows if r["verdict"] in {"supported", "hallucinated"}]
        hallucinated = [r for r in known if r["verdict"] == "hallucinated"]
        hallucination_rate = len(hallucinated) / len(known) if known else 0.0

        run_rates = defaultdict(lambda: {"hall": 0, "known": 0})
        for r in known:
            run_id = int(r["run_id"])
            run_rates[run_id]["known"] += 1
            if r["verdict"] == "hallucinated":
                run_rates[run_id]["hall"] += 1

        rates = []
        for run_id in sorted(run_rates):
            d = run_rates[run_id]
            rates.append(d["hall"] / d["known"] if d["known"] else 0.0)

        variance = stdev(rates)
        consistency = 1.0 - variance
        consistency = max(0.0, min(1.0, consistency))

        metrics[strategy] = {
            "num_claims": len(rows),
            "num_known_claims": len(known),
            "num_hallucinated_claims": len(hallucinated),
            "hallucination_rate": hallucination_rate,
            "consistency": consistency,
            "variance": variance,
            "run_rates": rates,
        }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"metrics": metrics}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

