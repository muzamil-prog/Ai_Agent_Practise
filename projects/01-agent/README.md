# 01 - Tool-Calling AI Agent

A minimal command-line AI agent built with Python and the OpenAI SDK. The agent can call tools in a loop until it has enough information to answer.

## Tools

| Tool | Purpose |
| --- | --- |
| `calculator` | Safe arithmetic evaluation |
| `get_current_time` | Current time in any IANA timezone |
| `read_text_file` | Read text files inside this repository |
| `list_files` | List repository directory contents |

File tools are sandboxed to the repository root and block `.env` and `.git`.

## Setup

```bash
cd projects/01-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your `OPENAI_API_KEY`. Optionally change `OPENAI_MODEL` (default: `gpt-4o-mini`).

## Run

```bash
python agent.py
```

Example prompts:

- `What is (1450 * 3) / 7?`
- `What time is it in Asia/Karachi?`
- `List the files in this project and summarize the README.`

## Tests

```bash
python -m unittest discover -s tests -v
```

## How it works

1. The user message is sent to the model along with tool schemas.
2. If the model requests tools, the agent executes them and appends results to the conversation.
3. The model is called again until it returns a normal answer (max 6 tool rounds per turn).

Conversation history is kept in memory for the duration of the session.
