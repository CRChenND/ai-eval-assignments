import argparse
import json
from pathlib import Path

from pipeline_utils import BASE_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot strategy comparison charts.")
    parser.add_argument(
        "--metrics",
        default=str(BASE_DIR / "results" / "analysis" / "metrics.json"),
        help="Metrics JSON path",
    )
    parser.add_argument(
        "--output-dir",
        default=str(BASE_DIR / "results" / "plots"),
        help="Directory for output plots",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise RuntimeError("matplotlib is required. Install via: pip install matplotlib") from err

    metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))["metrics"]
    strategies = list(metrics.keys())
    hallucination_rates = [metrics[s]["hallucination_rate"] for s in strategies]
    consistency_scores = [metrics[s]["consistency"] for s in strategies]

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 4))
    plt.bar(strategies, hallucination_rates)
    plt.xticks(rotation=20, ha="right")
    plt.title("Hallucination Rate by Strategy")
    plt.ylabel("Rate")
    plt.tight_layout()
    plt.savefig(out_dir / "hallucination_bar_chart.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.bar(strategies, consistency_scores)
    plt.xticks(rotation=20, ha="right")
    plt.title("Strategy Consistency Comparison")
    plt.ylabel("Consistency (1 - variance)")
    plt.tight_layout()
    plt.savefig(out_dir / "strategy_comparison.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()

