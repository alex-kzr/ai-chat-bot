# Feature: Project-Wide Python Refactoring

This plan describes a targeted refactoring of the Python codebase to reduce import-time side effects, separate infrastructure from orchestration, make runtime state explicit, and add quality gates around typing and tests. The plan is based on the current project structure, the existing documentation, and the `python*` skills focused on configuration, design patterns, error handling, observability, testing, and type safety.

## Phase 1: Configuration & Bootstrap (CB-01 to CB-03)

Stabilize application startup by replacing mutable module globals with explicit settings and bootstrap flow. This phase addresses the most fragile parts of the current code: `config.py` import-time validation and mutation, blocking model selection inside async code, and scattered logging setup.

## Phase 2: Runtime Services & State (RS-01 to RS-03)

Extract runtime responsibilities into focused services so Telegram handlers, Ollama access, agent orchestration, and conversation state are no longer tightly coupled. The goal is to make request flow easier to test, easier to evolve, and less dependent on hidden global state.

## Phase 3: Quality Gates & Safety (QG-01 to QG-03)

Add explicit contracts, better error boundaries, and automated checks around the refactored architecture. This phase closes the loop by making critical paths testable and by adding static and runtime validation that keeps the codebase consistent after the refactoring lands.
