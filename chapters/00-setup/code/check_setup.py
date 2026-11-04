"""Check that your computer is ready for the course.

Run: python3 check_setup.py
On a low-memory computer, run: python3 check_setup.py qwen2.5:3b
"""
import json
import os
import shutil
import sys
import urllib.request

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"
SMALL_MODEL = "qwen2.5:3b"
MIN_DISK_GB = 10
MIN_MEMORY_GB = 8
ADD_TOOL = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Add two numbers.",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
}


def call_ollama(path, body=None):
    """Call the Ollama server and return its JSON response."""
    data = json.dumps(body).encode() if body else None
    request = urllib.request.Request(OLLAMA + path, data, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)


def memory_gb():
    """Return total memory in GB, or None if this system doesn't report it."""
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30
    except (AttributeError, ValueError, OSError):
        return None


def chat(model, prompt, tools=None):
    body = {"model": model, "stream": False, "options": {"temperature": 0},
            "messages": [{"role": "user", "content": prompt}]}
    if tools:
        body["tools"] = tools
    return call_ollama("/api/chat", body)["message"]


def check_python():
    version = sys.version_info
    assert version >= (3, 12), f"You have {version.major}.{version.minor}. Install Python 3.12 or newer."
    return f"{version.major}.{version.minor}.{version.micro}"


def check_disk():
    free = shutil.disk_usage(".").free / 1e9
    assert free >= MIN_DISK_GB, f"Only {free:.0f} GB free. Free up at least {MIN_DISK_GB} GB."
    return f"{free:.0f} GB free"


def check_memory():
    total = memory_gb()
    if total is None:
        return "Not reported on this system. You need at least 8 GB."
    assert total >= MIN_MEMORY_GB or MODEL == SMALL_MODEL, (
        f"Only {total:.0f} GB. Run: ollama pull {SMALL_MODEL}, "
        f"then: python3 check_setup.py {SMALL_MODEL}"
    )
    return f"{total:.0f} GB"


def check_ollama():
    try:
        return "version " + call_ollama("/api/version")["version"]
    except OSError:
        raise AssertionError("Ollama isn't running. Open the Ollama app, or run: ollama serve")


def check_model():
    names = [m["name"] for m in call_ollama("/api/tags")["models"]]
    assert MODEL in names, f"{MODEL} isn't installed. Run: ollama pull {MODEL}"
    return MODEL


def check_answer():
    reply = chat(MODEL, "Reply with only the word ready.")["content"]
    assert reply.strip(), "The model returned an empty reply."
    return repr(reply.strip())


def check_tools():
    calls = chat(MODEL, "Use the add tool to add 2 and 3.", [ADD_TOOL]).get("tool_calls")
    assert calls, "The model didn't call the tool. Run this check again."
    return calls[0]["function"]["name"] + " was called"


CHECKS = [
    ("Python", check_python),
    ("Disk space", check_disk),
    ("Memory", check_memory),
]
MODEL_CHECKS = [
    ("Ollama", check_ollama),
    ("Model installed", check_model),
    ("Model answers", check_answer),
    ("Model uses tools", check_tools),
]


def run(label, check):
    try:
        print(f"PASS  {label}: {check()}")
        return True
    except Exception as error:
        print(f"FAIL  {label}: {error}")
        return False


def main():
    passed = sum(run(label, check) for label, check in CHECKS)
    blocked = False
    for label, check in MODEL_CHECKS:
        if blocked:
            print(f"SKIP  {label}: fix the failure above first")
        elif run(label, check):
            passed += 1
        else:
            blocked = True
    total = len(CHECKS) + len(MODEL_CHECKS)
    print(f"{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        MODEL = sys.argv[1]
    sys.exit(main())
