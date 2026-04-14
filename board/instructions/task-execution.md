# AGENT INSTRUCTIONS

You are an autonomous coding agent.

## Execution Workflow

Repeat the following loop:

1. Open `board/board.md`
2. Select the TOP task from "To Do" 
3. Move it to "In Progress" and update status in `board/tasks/`
4. Open corresponding task file in `board/tasks/`
5. Read and understand:
    - Purpose
    - Requirements
    - Definition of Done

6. Implement the task

7. Validate:
    - Follow "Validation Steps"
    - Ensure Definition of Done is satisfied

8. Update:
    - Move task to "Done" in `board/board.md` and update status in `board/tasks/`

9. Repeat

---

## Rules

- Only ONE task can be in progress
- Do NOT skip tasks
- Do NOT reorder tasks unless explicitly instructed
- Do NOT modify task scope

---

## If blocked

- Document the issue in the task file
- Move task back to "To Do"
- Optionally create a new task describing the blocker

---

## If new work is discovered

- DO NOT extend current task
- Create a NEW task
- Add it to:
    - `board/tasks.md`
    - `board/board.md`
    - create task file in `board/tasks/`

---

## Stability requirement

After EACH task:
- Project must remain runnable
- No broken functionality allowed