AL-04 - Implement agent loop core

Status

- [ ] To Do
- [ ] In Progress
- [x] Done

Purpose

Implement the main agent loop: LLM → JSON parsing → branch selection
(tool call or final answer) → repeat. The loop must not return a
response to the user until it receives {"final_answer": "..."}.

Context

This is the central task of the entire AL plan. The loop ties together
AL-01 (config), AL-02 (prompt), AL-03 (tools), and AL-05 (parser).

Key rule: the agent MUST NOT return a response to the user until the LLM
responds with {"final_answer": "..."}. Only final_answer is the
termination signal.

Requirements

-   Create src/agent/core.py with
    async def run_agent(task: str) -> AgentResult.
-   AgentResult: final_answer: str | None, steps: list[Step],
    stopped_reason: Literal["final", "max_steps", "error"].
-   Step: thought: str, action: str | None, args: dict | None,
    observation: str | None.
-   Loop algorithm:
    1.  Build system prompt: build_agent_prompt(list(TOOLS.values())) —
        tools are rendered into the prompt.
    2.  Initialize messages = [{"role": "user", "content": task}].
    3.  Iterate up to AGENT_MAX_STEPS:
        a.  Call LLM (_call_ollama(system_prompt, messages)) →
        raw_response: str.
        b.  Parse: parsed = parse_agent_output(raw_response).
        c.  If ParseError → one retry with correction message (see
        AL-05). If it fails again → stopped_reason="error", exit.
        d.  If FinalStep → store final_answer, stopped_reason="final",
        return result.
        e.  If ActionStep → do not return to user:
        -   Find tool in TOOLS[action]. If not found →
        observation = "[tool_error] unknown tool: <name>".
        -   Else: observation = await TOOLS[action].run(args).
        -   Record Step(thought, action, args, observation).
        -   Append to messages:
        {"role": "assistant", "content": raw_response} and
        {"role": "user", "content": f"Observation: {observation}"}.
        -   Continue loop.
    4.  After AGENT_MAX_STEPS without final_answer →
        stopped_reason="max_steps", return.
-   Log each iteration: thought, action, observation (INFO), raw
    response (DEBUG).

Implementation Notes

-   _call_ollama(system_prompt, messages) — private method: sends
    [{"role": "system", ...}] + messages to OLLAMA_URL/api/chat with
    AGENT_MODEL, AGENT_TEMPERATURE, stream=False.
-   Do not reuse ask_llm() — the agent requires a different model,
    temperature, and no system prompt deduplication.
-   Catch httpx errors in _call_ollama → stopped_reason="error".
-   If the tool is unknown, the loop continues — LLM receives the error
    observation and must self-correct.

Definition of Done

-   ☐ run_agent("What is 17*23?") returns final_answer="391",
    stopped_reason="final"
-   ☐ With AGENT_MAX_STEPS=5 and a 6-step task →
    stopped_reason="max_steps"
-   ☐ Unknown tool name → loop continues with [tool_error] in
    observation
-   ☐ Response is returned to user only when final_answer is received
-   ☐ Each step is logged at INFO level

Affected Files / Components

-   src/agent/core.py

Risks / Dependencies

-   Depends on AL-01, AL-02, AL-03, AL-05.
-   Risk: model may add text outside JSON — parser (AL-05) must handle
    this.
-   Risk: infinite loop if the model always returns action — mitigated
    by AGENT_MAX_STEPS.

Validation Steps

1.  asyncio.run(run_agent("What is 17*23?")) → final_answer="391", steps
    include calculator action.
2.  AGENT_MAX_STEPS=5 python -c "import asyncio; from src.agent.core import run_agent; r=asyncio.run(run_agent('do 6 things')); print(r.stopped_reason)"
    → "max_steps".
3.  Disable Ollama, run → stopped_reason="error", no traceback.
4.  Logs at INFO show each thought/action/observation.
