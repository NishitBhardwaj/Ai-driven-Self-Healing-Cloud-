# Coding/Code-Fixer Agent

## Purpose

The Coding/Code-Fixer Agent is responsible for:
- Using LLM to generate code
- Auto-detecting error patterns in code
- Suggesting solutions and fixes
- Providing explanations for why fixes work

## Responsibilities

1. **Code Generation**: Generates code based on descriptions
2. **Error Detection**: Analyzes stacktraces and error logs
3. **Fix Suggestions**: Provides actionable fixes with explanations
4. **Code Quality**: Ensures generated code follows best practices

## Functions

- `debug_code()` - Debug code issues using LLM
- `generate_code()` - Generate code from descriptions
- `llm_call()` - Make LLM API calls

## Input

- Stacktrace
- File path
- Error logs
- Code descriptions

## Output

- Root cause analysis
- Suggested fixes
- Generated code
- Explanations

## LLM Integration

Uses shared `llm.py` module supporting:
- OpenRouter (default)
- Google Gemini

## Usage

```python
from agent import CodingAgent

agent = CodingAgent()
agent.start()

# Debug code
result = agent.debug_code(
    stacktrace="Error message",
    file_path="app.py"
)

# Generate code
code = agent.generate_code(
    description="Create a REST API endpoint",
    language="python"
)
```

