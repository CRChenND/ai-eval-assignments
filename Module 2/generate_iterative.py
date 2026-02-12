from openrouter_client import call_openrouter, extract_text
from pipeline_utils import default_parser, read_prompt, utc_now_iso, write_json


def main() -> None:
    parser = default_parser("iterative")
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()

    base_prompt = read_prompt()
    outputs = []
    running_prompt = base_prompt

    for i in range(args.runs):
        completion = call_openrouter(
            model=args.model,
            prompt=running_prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        response = extract_text(completion)
        outputs.append(
            {
                "run_id": i + 1,
                "prompt": running_prompt,
                "response": response,
                "raw_completion": completion,
            }
        )
        # Lightweight prompt refinement from previous response.
        running_prompt = (
            base_prompt
            + "\n\nRefine your previous plan with stricter quantitative checks and fewer assumptions.\n"
            + f"Previous draft:\n{response[:2000]}"
        )

    write_json(
        args.output,
        {
            "strategy": "prompt_iteration",
            "model": args.model,
            "created_at": utc_now_iso(),
            "runs": args.runs,
            "outputs": outputs,
        },
    )


if __name__ == "__main__":
    main()

