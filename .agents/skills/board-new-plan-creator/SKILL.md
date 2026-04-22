---
name: board-new-plan-creator
description: Creation of a plan and tasks for new functionality based on a feature description and project context.
---

# Skill: board-new-plan-creator

## Description (when to use)

Use `board-new-plan-creator` when you need to break down new functionality into a plan and tasks: generate `plan.md`, `tasks.md`, task files in `board/tasks/`, and the Kanban board `board.md`.

## Input Data

Before starting, the agent must have:

- A description of the new feature from the prompt.
- Access to `docs/*` to understand the project context.
- (Optional) Jira ID if the feature is linked to a task.

## Execution Steps

1. **Analyze input data** — read `docs/*` (except `docs/cr/`), extract from the prompt or Jira: features, requirements, constraints.

2. **Planning** — break the feature into 2–3 phases, each with a clear goal and short description. Define tasks for each phase, ensuring they are atomic and independent.

For each phase create {phase-id} from the first letters, for example:
- Observability & Traceability → OT
- Hybrid Search → HS
- Cross-Encoder Reranking → CER
- Query Expansion → QE
- etc.

For each task in the phase:
- assign identifier {task_id}, which consists of {phase-id}_{task-order-number}
- assign a short task name {short-name}

3. **Create or update `board/plan.md`** — describe the feature and split it into phases with IDs and task ranges. Follow the template:

```
# Feature: <Feature Name>

<Short description of the feature>

## Phase 1: <Phase Name> (<First task ID of phase 1> to <Last task ID of phase 1>)
<Short description of phase 1>

## Phase 2: <Phase Name> (<First task ID of phase 2> to <Last task ID of phase 2>)
<Short description of phase 2>
```

Example of a completed plan:

```
# Feature: Conversation history for each user

This plan describes adding conversational memory to an AI chatbot. In the current implementation, the bot processes each message in isolation, sending only the system prompt and the current user message to the LLM. The goal is to preserve context between messages separately for each user.

## Phase 1: Pseudo-memory (PM-01 to PM-03)

We introduce in-memory dialogue storage, refactor the LLM call to support history, and integrate everything into the message handler. Each user gets an independent dialogue context identified by their numeric Telegram user ID.
```

4. **Create or update `board/tasks.md`** — for each phase list tasks with codes, short descriptions, and links to task files. Follow the template:

```
# 📋 Tasks — <Feature Name>
---

## Phase 1 — <Phase Name>

### <Task Code> <Task Name>
<Short task description>

### <Task Code> <Task Name>
<Short task description>

## Phase 2 — <Phase Name>

### <Task Code> <Task Name>
<Short task description>

---
```

Example of a completed task list:

```
# 📋 Tasks — Source Code Restructuring
---

## Phase 1 — Source Code Restructuring

### SR-01 Create src/ package directory
Create the `src/` directory with an `__init__.py` file so it becomes a proper Python package.
→ [SR-01-create-src-package.md](./tasks/SR-01-create-src-package.md)

### SR-02 Move source modules to src/
Move `config.py`, `prompts.py`, `llm.py`, `handlers.py`, and `bot.py` from the project root into `src/`.
→ [SR-02-move-source-modules.md](./tasks/SR-02-move-source-modules.md)

---

# 📋 Tasks — Pseudo-memory
---

## Phase 1 — Pseudo-memory

### PM-01 Create history storage module
Create `src/history.py` with in-memory per-user history storage: `get_history()`, `append_message()`, `clear_history()`.
→ [PM-01-history-storage.md](./tasks/PM-01-history-storage.md)

### PM-02 Refactor ask_llm() to support history
Update `src/llm.py` so that `ask_llm()` accepts a `history` list and sends the full context (system prompt + history + new message) to Ollama.
→ [PM-02-llm-history-support.md](./tasks/PM-02-llm-history-support.md)

### PM-03 Integrate history into message handler
Update `src/handlers.py` so that before calling `ask_llm()` the user's history is loaded, and after the call the assistant's response is saved.
→ [PM-03-handler-integration.md](./tasks/PM-03-handler-integration.md)

---
```

5. **Create task files** — for each task create `board/tasks/{task-id}_{task-short-name}.md` based on the task description template see below.

6. **Create or update `board/board.md`** — add all new tasks to the `To Do` section while preserving execution order. Follow the template:

```
# Kanban Board

## To Do
- <Task Code>: <Task Name>
- <Task Code>: <Task Name>

## In Progress
- (empty)

## Done
- (empty)
```

## ID Generation Rules

- Phase ID is formed from the first letters of the phase name:
    - `Observability & Traceability` → `OT`
    - `Hybrid Search` → `HS`
    - `Query Expansion` → `QE`

- Task ID: `{PHASE_ID}-{NN}`, for example `OT-01`.

- Tasks must be atomic: single responsibility, independently executable, testable.

## Output

The following must be created or updated:

- `board/plan.md`
- `board/tasks.md`
- `board/tasks/{task-id}_{task-short-name}.md` — for each task
- `board/board.md`

## Definition of Done

- [ ] `plan.md` contains the feature description and all phases with ID ranges.
- [ ] `tasks.md` contains all tasks with links to files.
- [ ] A file is created for each task based on the template see below in Task Desctiption Template
- [ ] All tasks are added to `To Do` in `board/board.md`.
- [ ] No vague formulations, no tasks mixing responsibilities.


## Task Description Template
```
# {task_id} - {title}

## Status
- [ ] To Do
- [ ] In Progress
- [ ] Done

## Purpose
Short description of why this task exists.

## Context
Background, links to related files, modules, or docs.

## Requirements
- Requirement 1
- Requirement 2
- Requirement 3

## Implementation Notes
- Suggested approach
- Constraints
- Important details

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Feature implemented
- [ ] Works as expected
- [ ] No regressions
- [ ] Code is clean and consistent
- [ ] Documentation is updated

## Affected Files / Components
- file1
- module/service
- api endpoint

## Risks / Dependencies
- Dependency 1
- Risk 1

## Validation Steps
1. Step 1
2. Step 2
3. Expected result

## Follow-ups (optional)
- Additional tasks if discovered during implementation
```

