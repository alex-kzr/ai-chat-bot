---
name: board-task-executor
description: Cycle through tasks from a task board, executing them as they are ready, and moving them through the board as they are completed, ensuring requirements and definition of done are met.
---

# SKILL: board-task-executor

## Description

This skill defines how an autonomous coding agent executes tasks from a task board, ensuring consistent progress, validation, and system stability.

---

## Behavior

You are an autonomous coding agent.

---

## Execution Workflow

Repeat the following loop:

1. **Analyze input data** — read `docs/*`

2. Open `board/board.md`

3. Select the TOP task from "To Do"

4. Move it to "In Progress" and update status in `board/tasks/`

6. Open corresponding task file in `board/tasks/`

7. Read and understand:

    * Purpose
    * Requirements
    * Definition of Done

8. Implement the task

9. Validate:

    * Follow "Validation Steps"
    * Ensure Definition of Done is satisfied

10. Update:

    * Move task to "Done" in `board/board.md`
    * Update status in `board/tasks/`

11. Repeat to next task

---

## Rules

* Only ONE task can be in progress
* Do NOT skip tasks
* Do NOT reorder tasks unless explicitly instructed
* Do NOT modify task scope

---

## If Blocked

* Document the issue in the task file
* Move task back to "To Do"
* Optionally create a new task describing the blocker

---

## If New Work Is Discovered

* DO NOT extend current task
* Create a NEW task
* Add it to:

    * `board/tasks.md`
    * `board/board.md`
    * Create task file in `board/tasks/`

---

## Stability Requirement

After EACH task:

* Project must remain runnable
* No broken functionality allowed
