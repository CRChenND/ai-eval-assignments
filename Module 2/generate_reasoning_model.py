from openrouter_client import call_openrouter, extract_text
from pipeline_utils import default_parser, read_prompt, utc_now_iso, write_json


SYSTEM_PROMPT = (
    "You are a rigorous reasoning assistant. Use explicit calculations and "
    "state uncertainty when data is missing."
)


def main() -> None:
    parser = default_parser("reasoning_model")
    args = parser.parse_args()

    prompt = read_prompt()
    completion = call_openrouter(
        model=args.model,
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    write_json(
        args.output,
        {
            "strategy": "reasoning_model",
            "model": args.model,
            "created_at": utc_now_iso(),
            "system_prompt": SYSTEM_PROMPT,
            "prompt": prompt,
            "response": extract_text(completion),
            "raw_completion": completion,
        },
    )


if __name__ == "__main__":
    main()

