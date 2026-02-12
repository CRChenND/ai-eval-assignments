import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pipeline_utils import BASE_DIR


def in_range(v: float, lo: float, hi: float) -> bool:
    return lo <= v <= hi


def pick_reference(sentence: str, refs: Dict) -> Optional[Tuple[str, List[float]]]:
    s = sentence.lower()
    if any(k in s for k in ["solar", "insolation"]):
        key = "surface_noon_insolation_equator_w_m2"
        return key, refs[key]["typical_range"]
    if any(k in s for k in ["irradiance", "orbit"]):
        key = "mars_solar_irradiance_w_m2"
        return key, refs[key]["typical_range"]
    if any(k in s for k in ["pressure", "pa", "kpa"]):
        key = "mars_average_surface_pressure_pa"
        return key, refs[key]["typical_range"]
    if any(k in s for k in ["temperature", "thermal", "cool", "heat"]):
        key = "mars_mean_surface_temp_c"
        return key, refs[key]["typical_range"]
    if any(k in s for k in ["gpu", "server", "rack", "power", "kw", "watt"]):
        key = "rack_8gpu_server_power_kw"
        return key, refs[key]["typical_range"]
    return None


def normalize_value(v: float, unit: str) -> float:
    if unit == "W":
        return v / 1000.0
    if unit == "MW":
        return v * 1000.0
    if unit == "kPa":
        return v * 1000.0
    return v


def main() -> None:
    parser = argparse.ArgumentParser(description="Fact-check extracted claims.")
    parser.add_argument(
        "--claims",
        default=str(BASE_DIR / "results" / "claims" / "claims.json"),
        help="Extracted claims JSON",
    )
    parser.add_argument(
        "--reference",
        default=str(BASE_DIR / "mars_reference.json"),
        help="Reference JSON",
    )
    parser.add_argument(
        "--output",
        default=str(BASE_DIR / "results" / "fact_check" / "fact_check.json"),
        help="Fact-check output JSON",
    )
    args = parser.parse_args()

    claims_obj = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    refs = json.loads(Path(args.reference).read_text(encoding="utf-8"))["references"]

    checked = []
    for c in claims_obj["claims"]:
        ref = pick_reference(c["text"], refs)
        if not ref or not c["numbers"]:
            checked.append({**c, "verdict": "unknown", "reason": "No mapped reference or numeric value."})
            continue

        ref_key, (lo, hi) = ref
        failures = []
        for n in c["numbers"]:
            v = normalize_value(n["value"], n["unit"])
            if not in_range(v, lo, hi):
                failures.append(f"{v} not in [{lo}, {hi}]")

        if failures:
            checked.append(
                {
                    **c,
                    "verdict": "hallucinated",
                    "reference_key": ref_key,
                    "reference_range": [lo, hi],
                    "reason": "; ".join(failures),
                }
            )
        else:
            checked.append(
                {
                    **c,
                    "verdict": "supported",
                    "reference_key": ref_key,
                    "reference_range": [lo, hi],
                    "reason": "Numeric values fall within reference range.",
                }
            )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"fact_checks": checked}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

