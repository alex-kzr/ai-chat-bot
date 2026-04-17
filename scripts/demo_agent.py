#!/usr/bin/env python3
"""Demo scenarios for the agentic loop.

Run with: python scripts/demo_agent.py (from project root)
"""

import asyncio
import sys
import os

# Add project root to path so src can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.core import run_agent
from src import config


SCENARIOS = [
    ("Calculator", "What is (123 + 77) * 4?"),
    ("HTTP Fetch", "Fetch https://example.com and report its HTTP status code."),
    ("Multi-tool", "Compute 456 * 789, then fetch https://httpbin.org/status/200 and tell me the status."),
]


async def run_demo() -> None:
    """Run all demo scenarios."""
    print(f"Agent Demo\n{'='*60}")
    print(f"Config: MAX_STEPS={config.AGENT_MAX_STEPS}, MODEL={config.AGENT_MODEL}, TEMP={config.AGENT_TEMPERATURE}\n")

    results = []
    for scenario_idx, (title, task) in enumerate(SCENARIOS, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {scenario_idx}: {title}")
        print(f"{'='*60}")
        print(f"Task: {task}\n")

        try:
            result = await run_agent(task)

            # Print steps
            for step_idx, step in enumerate(result.steps, 1):
                print(f"\nStep {step_idx}:")
                if step.thought:
                    print(f"  [THOUGHT] {step.thought}")
                if step.action:
                    args_str = str(step.args)[:100] if step.args else ""
                    print(f"  [ACTION] {step.action}({args_str})")
                if step.observation:
                    obs_preview = step.observation[:150]
                    if len(step.observation) > 150:
                        obs_preview += "..."
                    print(f"  [OBSERVATION] {obs_preview}")

            # Print final result
            print(f"\nResult:")
            if result.final_answer:
                print(f"  [ANSWER] {result.final_answer}")
            else:
                print(f"  [WARNING] No answer")
            print(f"  Status: {result.stopped_reason}")

            results.append((title, result.stopped_reason == "final", result.stopped_reason))
        except Exception as e:
            print(f"\n[ERROR] {type(e).__name__}: {e}")
            results.append((title, False, "exception"))

    # Summary
    print(f"\n\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    for title, success, reason in results:
        status = "[PASS]" if success else f"[FAIL] ({reason})"
        print(f"  {title}: {status}")

    # Exit with error if any scenario failed
    all_passed = all(success for _, success, _ in results)
    if not all_passed:
        print(f"\nSome scenarios failed. Exiting with code 1.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {type(e).__name__}: {e}")
        sys.exit(1)
