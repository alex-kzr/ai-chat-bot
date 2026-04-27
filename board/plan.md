# Feature: Security Hardening

This plan adds security controls to the Telegram AI chatbot to mitigate prompt injection, server-side request forgery (SSRF), unsafe tool usage, denial-of-service, and accidental disclosure of secrets in logs. The bot exposes an LLM, chat history, an agent loop with tools (`calculator`, `http_request`), and runs against a local Ollama instance, so the surface area covers user input, tool execution, retrieved web content, and observability.

The work preserves existing behavior, public bot commands, and the modular monolith architecture (`src/modules/*`, `src/agent/*`, `src/services/*`). Changes are minimal, configuration-driven where possible, and validated by focused tests.

## Phase 1: Tool & SSRF Hardening (TSH-01 to TSH-03)

Lock down the `http_request` tool against SSRF and unsafe targets (loopback, private RFC1918, link-local, cloud metadata endpoints), validate tool-call arguments via explicit schemas before execution, and re-check redirect targets so an attacker cannot bounce through a public host into an internal one.

## Phase 2: Input & DoS Protection (IDP-01 to IDP-03)

Add deterministic limits at the request boundary: maximum user input length in Telegram handlers, per-user rate limiting, and a centralized log sanitizer that masks secret-looking tokens (bot tokens, API keys, bearer headers, cookies) before they reach console or file logs.

## Phase 3: Prompt Injection Mitigation (PIM-01 to PIM-03)

Strengthen the trust boundary between system instructions, user input, chat history, and tool observations. Use unambiguous role-tagged delimiters in the prompt builder, wrap tool observations in an explicit "untrusted data" envelope, and detect/flag known instruction-override patterns ("ignore previous instructions", "reveal your system prompt", etc.) so the LLM cannot be silently steered by retrieved content.

## Phase 4: Security Tests & Tooling (STS-01 to STS-02)

Add a focused security test suite covering SSRF, prompt injection, oversized input, system-prompt leakage, and invalid tool calls. Wire static analysis (`bandit`, `pip-audit`, `ruff`) into the project tooling and document how to run them locally.
