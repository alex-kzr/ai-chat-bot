# AL-06 - Wire /agent Command into Telegram Handler

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Connect the agentic loop to Telegram: the `/agent <task>` command starts the loop, and the results of each step are sent to the user as they become available. The response to the user is sent **only after** `final_answer` is received.

## Context
`src/handlers.py` contains the aiogram Router. Adding `/agent` must not break the existing `handle_text` logic. The agentic loop returns `AgentResult` — the handler formats and sends the steps and the final answer.

## Requirements
- Register `@router.message(Command("agent"))` → `handle_agent(message)`.
- Parse the task from `message.text` after removing the `/agent` prefix. If the task is empty → reply with a usage hint.
- Call `run_agent(task)` — wait for the loop to complete (all steps are executed inside the loop).
- After completion, send the steps **sequentially** (MVP — after full completion, not in real time):
  - `🧠 Thought: <thought>` (if present)
  - `🛠 Action: tool_name(args)` (if present)
  - `👁 Observation: <observation>` (if present)
- Send the final result:
  - On `final_answer`: `✅ Answer: <answer>`.
  - On `stopped_reason != "final"`: `⚠️ Stopped: <reason>`.
- Keep `_keep_typing` active while the loop is running.
- Do **not** save the agent transcript into the user's chat history — agent runs are isolated.
- Truncate long observations to 4000 characters (`obs[:4000] + "..."`).

## Implementation Notes
- The handler should stay thin — only formatting and sending. Business logic belongs in `core.py`.
- If `result.stopped_reason == "max_steps"`, send the last available step + a warning.
- Do not duplicate `_handle_as_agent` logic — unify through a shared helper function if needed.
- Chunk messages: if `thought` > 4096 characters — truncate it.

## Definition of Done
- [x] `/agent` without arguments → usage hint
- [x] `/agent What is 12*15?` → sequence of 🧠/🛠/👁 messages, then ✅ with answer `180`
- [x] `stopped_reason="max_steps"` → ⚠️ message with the reason
- [x] Regular text (not `/agent`) → still handled by `handle_text`
- [x] Typing indicator stays active during the entire execution period

## Affected Files / Components
- `src/handlers.py`

## Risks / Dependencies
- Depends on AL-04, AL-05.
- Telegram rate limits: too many short messages in a row may trigger limits — keep the number of steps reasonable.
- With a large `AGENT_MAX_STEPS`, the user waits longer — there is no streaming in the MVP.

## Validation Steps
1. Send `/agent` (without arguments) → the bot replies with a usage message.
2. Send `/agent What is 12*15?` → a series of 🧠/🛠/👁 messages, and finally `✅ Answer: 180`.
3. Send a regular message `"Hi"` → handled by `handle_text`, history is preserved.
4. Check the logs: each agent step is logged at INFO before being sent to Telegram.
