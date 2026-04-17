# AL-03 - Create tools registry module

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Create an agent tools registry — a single place where available tools and their metadata are defined. The registry is used both for execution (loop) and for prompt generation (build_agent_prompt).

## Context
The agentic loop calls tools by name (`action` from the LLM JSON response). Each tool must:
- Have a unique name matching what the LLM provides in the `action` field.
- Have a `description` and `args_schema` — these are rendered into the system prompt (AL-02).
- Have a function `run(args: dict) -> str` — returns a string observation for the LLM.

## Requirements
- Create `src/agent/__init__.py` and `src/agent/tools.py`.
- Dataclass `ToolSpec`: fields `name: str`, `description: str`, `args_schema: dict`, `run: Callable[[dict], Coroutine[str]]`.
- `args_schema` — JSON Schema-style dict: `{field_name: {"type": str, "description": str, "required": bool}}`.
- Implement two MVP tools:
  - `calculator(args: {"expression": str}) -> str` — evaluates safe arithmetic expressions via `ast` (without `eval`). Supports `+, -, *, /, //, %, **`.
  - `http_request(args: {"url": str, "method": str}) -> str` — async GET/POST via `httpx`, returns `<status> <reason>\n\n<body[:2048]>`.
- `TOOLS: dict[str, ToolSpec]` — registry (key = tool name).
- All tools must be `async def` — loop calls `await tool.run(args)`.
- Errors inside tools must be caught and returned as a string `"[tool_error] <message>"`.

## Implementation Notes
- `calculator`: parse using `ast.parse(mode="eval")`, recursively walk `BinOp`, `UnaryOp`, `Constant`/`Num`. Everything else → `ValueError`.
- `http_request`: validate scheme (`http://` or `https://`), use `AGENT_TOOL_TIMEOUT` from config, `follow_redirects=True`.
- Both tools must return **only a string** — LLM will receive it as `Observation`.
- Do not import from `core.py` — only from `config.py`.

## Definition of Done
- [x] `src/agent/__init__.py` and `src/agent/tools.py` are created
- [x] `ToolSpec` dataclass is defined with all fields
- [x] `TOOLS` registry contains `calculator` and `http_request`
- [x] Each tool’s `args_schema` is suitable for prompt rendering
- [x] Errors are never raised from `run()` — only returned as a string
- [x] Unit test: `calculator` with `"2+2*3"` → `"8"`, with `"__import__(‘os’)"` → `[tool_error]`

## Affected Files / Components
- `src/agent/__init__.py`
- `src/agent/tools.py`

## Risks / Dependencies
- `calculator` AST walker must be secure — evaluating arbitrary expressions via `eval` is a common vulnerability.
- `httpx` is already a project dependency — no new packages required.
- Field names in `ToolSpec` must match what `build_agent_prompt` expects in AL-02.

## Validation Steps
1. `await TOOLS["calculator"].run({"expression": "2+2*3"})` → `"8"`.
2. `await TOOLS["calculator"].run({"expression": "__import__('os').system('x')"})` → `"[tool_error] ..."`.
3. `await TOOLS["http_request"].run({"url": "https://example.com"})` → string with status code and body.
4. `await TOOLS["http_request"].run({"url": "ftp://bad"})` → `"[tool_error] URL must use http or https scheme"`.
5. `[{"name": t.name, "description": t.description, "args_schema": t.args_schema} for t in TOOLS.values()]` — structure is suitable for `build_agent_prompt`.
