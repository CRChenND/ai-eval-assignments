import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from pipeline_utils import BASE_DIR


NUM_UNIT_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*(kW|W|MW|C|°C|Pa|kPa|W/m2|W/m\^2|%)?")


def split_sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def claim_type(sentence: str) -> str:
    s = sentence.lower()
    if any(k in s for k in ["power", "watt", "kw", "mw", "solar", "energy"]):
        return "power"
    if any(k in s for k in ["thermal", "cool", "temperature", "heat", "celsius"]):
        return "thermal"
    if any(k in s for k in ["deploy", "landing", "transport", "step", "procedure"]):
        return "deployment"
    return "other"


def extract_from_text(strategy: str, run_id: int, text: str) -> List[Dict]:
    out = []
    for sentence in split_sentences(text):
        nums = NUM_UNIT_RE.findall(sentence)
        if not nums and claim_type(sentence) == "other":
            continue
        out.append(
            {
                "strategy": strategy,
                "run_id": run_id,
                "type": claim_type(sentence),
                "text": sentence,
                "numbers": [{"value": float(v), "unit": u or ""} for v, u in nums],
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract claims from generation outputs.")
    parser.add_argument(
        "--input-dir",
        default=str(BASE_DIR / "results" / "raw"),
        help="Directory containing strategy output JSON files",
    )
    parser.add_argument(
        "--output",
        default=str(BASE_DIR / "results" / "claims" / "claims.json"),
        help="Output JSON file",
    )
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    records = []
    for fp in sorted(in_dir.glob("*.json")):
        obj = json.loads(fp.read_text(encoding="utf-8"))
        strategy = obj.get("strategy", fp.stem)
        if "outputs" in obj:
            for run in obj["outputs"]:
                records.extend(extract_from_text(strategy, int(run["run_id"]), run.get("response", "")))
        else:
            records.extend(extract_from_text(strategy, 1, obj.get("response", "")))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"claims": records}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

