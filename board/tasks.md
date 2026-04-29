# 📋 Tasks — Agent Loop Safety and Streaming Protection
---

## Phase 1 — Guardrails and Watchdogs

### GW-01 Define runtime safety settings and stop reasons
Add explicit configuration and runtime contracts for agent safety limits: max agent steps, max parser retries, max repeated answers, max identical tool calls, max loop iterations, max response length, LLM response timeout, and stream timeout. Extend the agent result model with precise termination reasons for each guardrail path.
→ [GW-01_runtime-safety-settings.md](./tasks/GW-01_runtime-safety-settings.md)

### GW-02 Detect repeated outputs and cyclic agent states
Add loop-detection logic that compares consecutive answers, reasoning blocks, and state signatures so the runtime can detect when generation is no longer making progress. Abort with a controlled failure once repeat or cycle thresholds are exceeded.
→ [GW-02_repeat-and-cycle-detection.md](./tasks/GW-02_repeat-and-cycle-detection.md)

### GW-03 Add stream watchdog and timeout aborts
Protect streaming generation with a watchdog that aborts when no new chunks arrive within the configured window, when identical chunks/tokens repeat excessively, or when the stream never reaches a terminal close event. Ensure cleanup is deterministic and surfaced as a typed runtime failure.
→ [GW-03_stream-watchdog.md](./tasks/GW-03_stream-watchdog.md)

### GW-04 Prevent infinite tool-call retries
Add tool-loop protection so the agent cannot invoke the same tool forever with identical or trivially repeated arguments. Require retries to carry a changed input or an explicit retry reason, and terminate after a bounded retry count.
→ [GW-04_tool-loop-protection.md](./tasks/GW-04_tool-loop-protection.md)

## Phase 2 — Parser and Finalization Hardening

### PF-01 Harden JSON extraction and schema validation
Improve the parser so it can extract JSON from markdown-wrapped or noisy model output, validate the top-level schema reliably, and distinguish action steps, final answers, and invalid responses without ambiguous fallthrough behavior.
→ [PF-01_json-parser-hardening.md](./tasks/PF-01_json-parser-hardening.md)

### PF-02 Enforce final-answer completion with bounded retries
Make final-answer completion a strict runtime rule: invalid or incomplete responses trigger controlled retries, repeated invalid output terminates the run, and successful completion always flows through `final_answer` rather than silently accepting partial or malformed terminal responses.
→ [PF-02_final-answer-enforcement.md](./tasks/PF-02_final-answer-enforcement.md)

### PF-03 Align prompt and runtime with model-agnostic stop conditions
Review and update stop sequences, EOS handling, max-token boundaries, and prompt-format assumptions so the runtime behaves consistently across Ollama, vLLM, LM Studio, and other OpenAI-compatible backends even when model chat templates differ.
→ [PF-03_model-agnostic-stop-conditions.md](./tasks/PF-03_model-agnostic-stop-conditions.md)

## Phase 3 — Diagnostics and Validation

### DV-01 Add structured loop diagnostics and watchdog telemetry
Extend structured logging to capture prompt snapshots, raw LLM output, streamed chunks, loop iterations, similarity scores, parser failures, retry reasons, and the final termination reason so loop-related failures are diagnosable after the fact.
→ [DV-01_loop-diagnostics-and-telemetry.md](./tasks/DV-01_loop-diagnostics-and-telemetry.md)

### DV-02 Add unit tests for safety protections
Add focused unit tests for repeated-output detection, repeated-tool detection, malformed JSON handling, final-answer enforcement, response-size limits, and stream timeout / repeated-chunk watchdog logic.
→ [DV-02_unit-tests-for-safety-protections.md](./tasks/DV-02_unit-tests-for-safety-protections.md)

### DV-03 Add integration scenarios for stuck-model failures
Create integration-style scenarios with scripted model behavior that reproduces infinite text repetition, infinite identical tool calls, malformed JSON spam, and non-terminating streams. Each scenario must verify that the runtime aborts cleanly with the expected stop reason and diagnostics.
→ [DV-03_integration-stuck-model-scenarios.md](./tasks/DV-03_integration-stuck-model-scenarios.md)

---
