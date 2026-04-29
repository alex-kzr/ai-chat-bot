# Feature: Agent Loop Safety and Streaming Protection

This plan hardens the agent runtime against infinite generation, repeated tool loops, malformed structured output, and streams that never finish when using local or OpenAI-compatible LLM backends. The current architecture already has an iterative agent loop, a strict parser, and structured logging, but it still needs stronger runtime guardrails so one bad model response cannot keep the agent stuck forever.

The goal is to guarantee controlled termination across Ollama, vLLM, LM Studio, and other OpenAI-compatible gateways without coupling the fix to a single model family. The implementation must add hard runtime limits, detect repeated or cyclic states, enforce final-answer completion rules, and produce diagnostics that make failures easy to investigate. The work also includes unit and integration coverage for the main failure scenarios described in the prompt.

## Phase 1: Guardrails and Watchdogs (GW-01 to GW-04)

Introduce the hard runtime boundaries that keep one agent run finite: configurable step/retry/tool-call/response-size limits, stream and response timeouts, repeated-output detection, repeated-tool detection, and watchdog-based abort paths when the model stops making progress.

## Phase 2: Parser and Finalization Hardening (PF-01 to PF-03)

Strengthen the structured-output contract so the agent can recover from noisy markdown/JSON, reject invalid action payloads deterministically, enforce final-answer completion, and terminate with a controlled error after bounded retries instead of re-prompting forever.

## Phase 3: Diagnostics and Validation (DV-01 to DV-03)

Complete the feature with detailed loop diagnostics, targeted unit tests for the protection mechanisms, and integration scenarios that simulate infinite text repetition, repeated tool calls, malformed JSON, and non-terminating streams.
