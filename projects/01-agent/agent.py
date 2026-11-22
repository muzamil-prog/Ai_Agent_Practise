import os
import sys

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from tools import TOOL_SPECS, execute_tool

SYSTEM_PROMPT = (
    "You are a helpful AI assistant with access to tools. "
    "Use the calculator for arithmetic, the time tool for dates and times, "
    "and the file tools only when the user asks about files in the repository. "
    "Never invent tool results. If a tool fails, explain the error briefly."
)

MAX_TOOL_ROUNDS = 6
MAX_TOOL_RESULT_CHARS = 12000


def run_agent(client, model, messages):
    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_SPECS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        for tool_call in message.tool_calls:
            result = execute_tool(tool_call.function.name, tool_call.function.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result[:MAX_TOOL_RESULT_CHARS],
                }
            )

    return "Stopped: the agent reached the tool-call limit for this turn."


def main():
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY. Copy .env.example to .env and add your key.")
        return 1

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"AI Agent ready (model: {model}). Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})

        try:
            answer = run_agent(client, model, messages)
        except OpenAIError as exc:
            print(f"Agent error: {exc}\n")
            messages.pop()
            continue

        print(f"Agent: {answer}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
