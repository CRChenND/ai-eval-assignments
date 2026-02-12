from openrouter_client import call_openrouter, extract_text
from pipeline_utils import default_parser, read_prompt, utc_now_iso, write_json


def main() -> None:
    parser = default_parser("zero_shot")
    args = parser.parse_args()

    prompt = read_prompt()
    completion = call_openrouter(
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    write_json(
        args.output,
        {
            "strategy": "zero_shot",
            "model": args.model,
            "created_at": utc_now_iso(),
            "prompt": prompt,
            "response": extract_text(completion),
            "raw_completion": completion,
        },
    )


if __name__ == "__main__":
    main()

