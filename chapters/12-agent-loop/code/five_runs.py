"""Provided measuring tool: run the agent five times per prompt and count the right answers.

You don't need to read this file closely. It runs the run_agent function you already know,
at temperature 0.7, and hides the step lines so the results fit on one screen.
"""
import contextlib
import io

import agent

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"
PROMPTS = {
    "Original prompt": agent.SYSTEM,
    "Longer prompt": agent.SYSTEM + " Files are in the workspace. List a folder before reading "
                                    "from it. Do not ask the user for help. Keep using tools "
                                    "until you can answer.",
}


def lively_chat(messages):
    return agent.chat(messages, temperature=0.7)


for label, prompt in PROMPTS.items():
    agent.SYSTEM = prompt
    right = 0
    print(label)
    for run in range(1, 6):
        steps = io.StringIO()
        with contextlib.redirect_stdout(steps):
            answer = agent.run_agent(QUESTION, chat=lively_chat)
        right += "380" in answer
        tools_used = steps.getvalue().count("[step")
        print(f"  Run {run}: {tools_used} tool calls. Ends: {answer[-40:]!r}")
    print(f"  Reached 380: {right}/5")
