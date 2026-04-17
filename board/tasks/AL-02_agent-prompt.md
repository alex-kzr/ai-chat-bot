# AL-02 - Build agent system prompt with tools injection

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Create an agent system prompt that explicitly describes to the LLM: which tools are available (with arguments), what response format to follow, and how the loop operates. This serves as the primary safeguard against unstable JSON output.

## Context
The agent follows the ReAct (Reason + Act) pattern. The LLM **must** see in the system prompt:
1. The full list of available tools with names, descriptions, and argument schemas.
2. The exact JSON response format for both cases (tool call / final answer).
3. The loop rules: thought → action → observation → repeat → final answer.

Without this, the model does not know what tools exist or how to call them, which breaks the entire loop.

## Requirements
- Function `build_agent_prompt(tools: list[ToolSpec]) -> str` in `src/prompts.py`.
- The prompt **must** include:
  - **Tools section**: a numbered list with `name`, `description`, full `args_schema` for each tool.
  - **Output Format section**: both valid JSON formats with examples:
    ```json
    {"thought": "...", "action": "tool_name", "args": {...}}
    ```
    ```json
    {"final_answer": "..."}
    ```
  - **Loop Rules**: explicit prohibition of any text outside the JSON object, and prohibition of fabricating observations.
  - **Observation Format**: how the system passes tool results (`Observation: <result>`).
- The prompt accepts tools as a parameter and does not hardcode them — single source of truth from registry (AL-03).
- Prompt size ≤ 800 tokens (~3200 characters).

## Implementation Notes
- `_format_tools(tools)` should render for each tool:
  ```
  1. **calculator**
     Description: Evaluate safe arithmetic expressions
     Args: {"expression" (string): Arithmetic expression to evaluate}
  ```
- Add 1–2 few-shot examples of interaction (task → thought/action → observation → final_answer), clearly wrapped with `## Example`.
- Prompt must be in English (models follow English instructions better).
- `_format_tools` should accept both `list[ToolSpec]` and `list[dict]` — for flexibility.

## Definition of Done
- [x] `build_agent_prompt(tools)` added/updated in `src/prompts.py`
- [x] Prompt contains sections: Tools, Output Format, Loop Rules, Example
- [x] Both JSON formats are explicitly shown with examples
- [x] Calling with real `TOOLS.values()` renders a readable tools section
- [x] Prompt does not exceed 800 tokens
- [x] Unit test: `build_agent_prompt([mock_tool])` contains tool name and both JSON formats

## Affected Files / Components
- `src/prompts.py`

## Risks / Dependencies
- Depends on `ToolSpec` format from AL-03 (coordinate field names).
- Risk: prompt too long consumes context — keep ≤ 800 tokens.
- Risk: model ignores formatting — test with real `AGENT_MODEL`.

## Validation Steps
1. `from src.prompts import build_agent_prompt; from src.agent.tools import TOOLS; print(build_agent_prompt(list(TOOLS.values())))` — Tools and Output Format sections are visible.
2. Output contains both JSON formats (`"action"` and `"final_answer"`).
3. Output includes `calculator` and `http_request` with their arguments.
4. String length ≤ 3200 characters.
