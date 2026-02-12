from openrouter_client import call_openrouter, extract_text
from pipeline_utils import default_parser, read_prompt, utc_now_iso, write_json


COT_SUFFIX = """

Before final answer, reason through the task step by step.
Make intermediate calculations explicit and include units.
Then provide a concise final deployment recommendation.
"""


def main() -> None:
    parser = default_parser("cot")
    args = parser.parse_args()

    prompt = read_prompt() + "\n" + COT_SUFFIX.strip() + "\n"
    completion = call_openrouter(
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    write_json(
        args.output,
        {
            "strategy": "chain_of_thought",
            "model": args.model,
            "created_at": utc_now_iso(),
            "prompt": prompt,
            "response": extract_text(completion),
            "raw_completion": completion,
        },
    )


if __name__ == "__main__":
    main()

