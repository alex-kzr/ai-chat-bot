# AL-07 - Demo scenarios & end-to-end validation

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide a reproducible way to validate the entire agentic loop without Telegram: system prompt with tools, JSON parsing, tool execution, and looping until `final_answer`.

## Context
A CLI demo is the fastest way to verify that the loop, tools, parser, and step cap work correctly together. It also serves as living documentation for reviewers.

## Requirements
- Create `scripts/demo_agent.py` with `asyncio.run(main())`.
- Run 3 scenarios sequentially:
  1. **Calculator only** — `"What is (123 + 77) * 4?"` → expected `final_answer` contains `800`.
  2. **HTTP only** — `"Fetch https://example.com and report its HTTP status code."`.
  3. **Multi-tool chain** — `"Calculate 100 + 23, then fetch https://httpbin.org/get and report both the arithmetic result and the URL from the response."`.
- For each scenario output:
  - Task title.
  - Each `Step`: thought / action+args / observation.
  - Final `final_answer` or `stopped_reason`.
- Exit with code `1` if at least one scenario finishes with `stopped_reason == "error"`.
- Print ASCII separators between scenarios for readability.

## Implementation Notes
- Store scenarios in a list `[(title, task), ...]` for easy extensibility.
- Do not override `AGENT_MAX_STEPS` — respect configuration from env.
- Simple formatting: `[THOUGHT]`, `[ACTION]`, `[OBS]`, `[ANSWER]`, `[STOPPED]` prefixes.
- Prerequisite: Ollama is running, model `AGENT_MODEL` is loaded (`ollama pull qwen3:4b`).

## Definition of Done
- [x] Script runs end-to-end against local Ollama
- [x] Scenario 1: `final_answer` contains `800`
- [x] Scenario 2: `final_answer` contains the page HTTP status code
- [x] Scenario 3: loop uses both tools
- [x] When `stopped_reason="error"` the script exits with code `1`
- [x] Documentation or README references the script

## Affected Files / Components
- `scripts/demo_agent.py`

## Risks / Dependencies
- Depends on AL-04, AL-05 (entire pipeline must work).
- Requires running Ollama with loaded `AGENT_MODEL` — document this prerequisite.
- Scenario 3 (multi-tool) is most sensitive to prompt quality from AL-02.

## Validation Steps
1. `ollama pull qwen3:4b && python scripts/demo_agent.py` — all three scenarios complete.
2. Scenario 1: output shows `[ACTION] calculator`, result `800`.
3. Scenario 2: output shows `[ACTION] http_request`, `final_answer` mentions status.
4. Scenario 3: output shows both tools (`calculator` and `http_request`).
5. Stop Ollama → script exits with code `1` and prints an error, without traceback.

