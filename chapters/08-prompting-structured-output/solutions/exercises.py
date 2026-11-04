"""Chapter 08 exercises, solved."""
import json


def build_prompt(task, context, output_format):
    return f"Task: {task}\nContext: {context}\nFormat: {output_format}"


def with_examples(instructions, examples):
    lines = [instructions]
    for message, label in examples:
        lines.append(f"Message: {message} Label: {label}")
    return "\n".join(lines)


def final_answer(reply):
    return reply.strip().splitlines()[-1].strip()


def parse_json(reply):
    text = reply.strip().removeprefix("```json").removesuffix("```")
    return json.loads(text)


def label_schema(labels):
    return {
        "type": "object",
        "properties": {"label": {"type": "string", "enum": labels}},
        "required": ["label"],
    }
