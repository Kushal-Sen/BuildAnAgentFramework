"""Worked answers for the chapter 09 exercises."""


def ask_model(messages, chat):
    reply = chat(messages)
    messages.append({"role": "assistant", "content": reply})
    return reply


def give_result(messages, text):
    messages.append({"role": "user", "content": text})


def play_session(question, chat, results):
    messages = [{"role": "user", "content": question}]
    for result in results:
        ask_model(messages, chat)
        give_result(messages, result)
    return ask_model(messages, chat)


def workflow_prompt(question, files):
    lines = [f"{name}: {files[name]}" for name in sorted(files)]
    return question + "\n\n" + "\n".join(lines)


def pick_shape(needs_outside_facts, steps_known):
    if not needs_outside_facts:
        return "single call"
    if steps_known:
        return "workflow"
    return "agent"
