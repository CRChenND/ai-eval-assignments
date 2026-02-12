import json
from pathlib import Path

from openrouter_client import call_openrouter, extract_text
from pipeline_utils import BASE_DIR, default_parser, read_prompt, utc_now_iso, write_json


def build_evidence_block() -> str:
    ref = json.loads((BASE_DIR / "mars_reference.json").read_text(encoding="utf-8"))
    lines = ["Reference facts (use these ranges for validation):"]
    for key, val in ref["references"].items():
        rng = val.get("typical_range")
        lines.append(f"- {key}: {rng} | note: {val.get('note', '')}")
    return "\n".join(lines)


def main() -> None:
    parser = default_parser("tool_augmented")
    parser.add_argument(
        "--evidence-file",
        default=str(Path(BASE_DIR) / "mars_reference.json"),
        help="Reference file used for retrieval augmentation",
    )
    args = parser.parse_args()

    prompt = (
        read_prompt()
        + "\n\n"
        + build_evidence_block()
        + "\n\nCite which reference key supports each numeric claim."
    )

    completion = call_openrouter(
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    write_json(
        args.output,
        {
            "strategy": "tool_augmented",
            "model": args.model,
            "created_at": utc_now_iso(),
            "evidence_source": args.evidence_file,
            "prompt": prompt,
            "response": extract_text(completion),
            "raw_completion": completion,
        },
    )


if __name__ == "__main__":
    main()

