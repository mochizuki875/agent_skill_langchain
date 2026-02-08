# Agent Skill with LangChain
LangChain Agent that utilize multiple skills to perform tasks.
Agent skills are included in the `SKILLS` directory.

- [LangChain Skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)

Update the project's environment.
```bash
uv sync
```

Run the Agent.
```bash
uv run ./main.py
```

## Environment Variables
.env
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<API_KEY>
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=<PROJECT_NAME>
MODEL_BASE_URL=http://127.0.0.1:11434
MODEL_NAME=gpt-oss:20b
LLM_PROVIDER=ollama
```