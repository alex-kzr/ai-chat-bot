# NEW PLAN WORKFLOW

This document defines how to generate a new plan and tasks from input sources.

## Trigger

This workflow is used when:
- A prompt describes new functionality
- A roadmap is provided (e.g. docs/roadmap.md)
- New feature set is requested

---

## Step 1 - Analyze input

Read:
- docs/*
- prompt description

Extract:
- features
- requirements
- constraints

---

## Step 2 - Update plan.md

- Create file in `board/plan.md` with extracted phases and following structure e.g.:
```
# Architecture Overhaul: Autonomous AI & Robust Supervision

This plan describes the transition to an "Advanced" architecture where human and scheduled inputs are unified, and the system becomes more resilient through active process supervision.

## Phase 1: Infrastructure & Supervisor (IS-01 to IS-03)
We will standardize the lifecycle of all independent processes and implement a Supervisor in the Orchestrator to monitor and auto-restart crashed components.

## Phase 2: Autonomous AI Queries (AAQ-01 to AAQ-03)
We will turn existing cron-based notifications into full AI tasks.
- **Data Reuse**: The existing `reminderMessage` field in the `cron_schedules` table will store the AI query.
- **Workflow**: When a cron job fires, it will emit a `synthetic_goal` event.
- **Statefulness**: Each run is assigned a unique `UUID` (taskId) to reuse existing storage/memory structures.

```
- Break work into phases
- Each phase must have:
    - clear goal
    - short description

---

## Step 3 - Update tasks.md

- Create file in `board/tasks.md` with the following structure e.g.:
```
# 📋 Tasks — Architecture Overhaul
---

## Phase 1 — Infrastructure & Supervision

### IS-01 Standardize BaseProcess Lifecycle
Add heartbeats and health reporting to the common process base class.
→ [IS-01_BASE_PROCESS_LIFECYCLE.md](./tasks/IS-01_BASE_PROCESS_LIFECYCLE.md)

### IS-02 Implement Process Supervisor
Add auto-restart and crash tracking to Orchestrator.
→ [IS-02_PROCESS_SUPERVISOR.md](./tasks/IS-02_PROCESS_SUPERVISOR.md)

### IS-03 CLI Interactive Mode
Enable direct stdin testing for all services.
→ [IS-03_CLI_INTERACTIVE_MODE.md](./tasks/IS-03_CLI_INTERACTIVE_MODE.md)

---

## Phase 2 — Autonomous AI Queries

### AAQ-01 CronManager AI Query Support
Trigger `event.cron.ai_query` using the `reminderMessage` as the query text.
→ [AAQ-01_CRON_AI_QUERY.md](./tasks/AAQ-01_CRON_AI_QUERY.md)

### AAQ-02 Synthetic Goal Ingestion (Stateful)
Implement Orchestrator handler for cron events. Assign unique `taskId` for each run.
→ [AAQ-02_SYNTHETIC_GOAL_INGESTION.md](./tasks/AAQ-02_SYNTHETIC_GOAL_INGESTION.md)
```
- For each phase generate a unique id from the first letters of the **phase name** (e.g. for "Observability & Traceability" → OT, for "Hybrid Search" → HS, for "Cross-Encoder Reranking" → CER, for "Query Expansion" → QE)
- Break each phase into tasks
- Each task must:
    - be small
    - be executable independently
    - have unique id ({phase_id}-XX-{short-name}, e.g. AO-01-cron_ai-query, AO-02-synthetic_goal_ingestion)
    - link to file with task description (e.g. tasks/AO-01-cron_ai-query.md)

---

## Step 4 - Create task files

For EACH task:
- Create file in `board/tasks/` ( e.g. `board/tasks/AO-01-cron_ai-query.md`)
- Use template from `board/tasks/_template.md`

---

## Step 5 - Update board.md

- Create file in `board/board.md` with the following structure:
``` 
# BOARD

## To Do
- IS-01: Standardize BaseProcess lifecycle
- AAQ-01: Implement cron AI query

## In Progress
- (empty)

## Done
- (empty)
```


- Add all new tasks to "To Do"
- Keep execution order

---

## Rules

- Tasks must be atomic (small)
- No vague tasks
- No mixed responsibilities
- Each task must be testable

---

## Important

DO NOT:
- Skip task file creation
- Put logic directly into plan.md
- Create oversized tasks

---

## Result

After execution:
- plan.md updated
- tasks.md updated
- board.md populated
- task files created

System becomes ready for execution by agent