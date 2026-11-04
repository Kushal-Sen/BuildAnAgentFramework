# Chapter 06: Your first model call

**Time:** about 1.5 hours. **You'll build:** a `chat` function that talks to an AI model from your
own Python code.

## Where we are

In chapter 05, you made HTTP requests to Ollama, but only to ask about the server. Now you'll ask
the model itself a question. This is the moment your code starts talking to an AI.

## Run it

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. Then, from `chapters/06-first-model-call/code`, run:

```bash
python3 first_call.py
```

This is real output from `qwen2.5:7b`. Your replies will be different:

```text
1. One question
Python is a high-level, general-purpose programming language.
2. A system message
Arr! Python be a programming language, matey!
3. A conversation
Yellow.
4. Streaming
['Welcome', ' to', ' your', ' learning', ' journey', '!']
Welcome to your learning journey!
5. Two puzzles
Same question, three times: ['Sputnik', 'Purrfectly', 'Moonwhisper']
You didn't provide your name in the question.
```

Open [code/first_call.py](code/first_call.py) and follow along.

## The `chat` function

Calling a model is an HTTP request, just like the ones in chapter 05:

```python
def chat(messages, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]
```

Line by line:

1. `body` holds what you're sending: the model, the conversation and your settings.
2. `requests.post` sends it to Ollama. Models can be slow, so the timeout is long.
3. `raise_for_status` stops with an error if the status code shows a failure, such as 404.
4. The reply text is inside the JSON, at `["message"]["content"]`.

You'll use this function for the rest of the course.

## Messages

You send a model a list of **messages**. This is the list of dictionaries from chapter 02. Each one
has a **role**:

| Role | Who it's from | What it does |
|---|---|---|
| `user` | The person | Asks or says something |
| `assistant` | The model | A reply the model gave |
| `system` | You, the developer | Sets the rules for the conversation |

Here's the simplest call, with one `user` message:

```python
question = {"role": "user", "content": "What is Python? Reply in one short sentence."}
print(chat([question]))
```

```text
Python is a high-level, general-purpose programming language.
```

## System messages

A `system` message sets instructions before the conversation starts:

```python
pirate = {"role": "system",
          "content": "You always talk like a pirate, and you start every reply with Arr! "
                     "Keep your reply to one short sentence."}
print(chat([pirate, question]))
```

```text
Arr! Python be a programming language, matey!
```

Clear, specific instructions work best. Our first attempt, "You are a pirate", gave a plain answer
with no pirate voice at all, so we made it more specific.

## Conversations

To continue a conversation, you send all of it:

```python
messages = [
    {"role": "user", "content": "Suggest a fruit. Reply with one word."},
    {"role": "assistant", "content": "Mango"},
    {"role": "user", "content": "What color is it? Reply in one short sentence."},
]
print(chat(messages))
```

```text
Yellow.
```

The word "it" only makes sense because the earlier messages are included.

## Streaming

A long reply can take a while. With **streaming**, you get it piece by piece as it's written.
Set `stream` to `True`, and Ollama sends one line of JSON for each piece. A generator from chapter 04
is perfect for this:

```python
def stream_chat(messages):
    """Send a conversation to the model, and yield its reply piece by piece."""
    body = {"model": MODEL, "messages": messages, "stream": True}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180, stream=True)
    response.raise_for_status()
    for line in response.iter_lines():
        yield json.loads(line)["message"]["content"]
```

```text
['Welcome', ' to', ' your', ' learning', ' journey', '!']
Welcome to your learning journey!
```

## Two puzzles

You now have a working model call, but two things may surprise you. **Before you run this part,
predict what will happen.**

1. If you ask for a cat name three times, will you get the same answer?
2. If you tell the model your name, then ask for it in a second call, will it remember?

```python
name = {"role": "user", "content": "Suggest an unusual name for a cat. Reply with only the name."}
print("Same question, three times:", [chat([name]) for _ in range(3)])
chat([{"role": "user", "content": "My name is Asha."}])
print(chat([{"role": "user", "content": "What is my name? Reply in one short sentence."}]))
```

```text
Same question, three times: ['Sputnik', 'Purrfectly', 'Moonwhisper']
You didn't provide your name in the question.
```

Why does the same question give different answers? Why did it forget your name? You'll find out
in the next chapter.

## Reading errors

These are real errors:

| What happened | What you see | The fix |
|---|---|---|
| The model name is wrong | `requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://127.0.0.1:11434/api/chat` | Check the name with `ollama list` |
| Ollama isn't running | `requests.exceptions.ConnectionError: HTTPConnectionPool(...)` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You typed the wrong key | `KeyError: 'message'` | Print the response to see its real shape |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py) and complete the five TODOs. Together,
they build the pieces of a model call:

1. `user_message`: build a message.
2. `with_system`: add a system message.
3. `build_body`: build the request body.
4. `reply_text`: read the reply.
5. `join_stream`: join streamed pieces.

Then check your work:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Sending a single dictionary instead of a list of messages.
- Writing vague system messages. Be specific about what you want.
- Forgetting `stream=True` in both the body and `requests.post` when streaming.
- Expecting the same answer every time.

## Recap

- A model call is an HTTP request with a list of messages.
- Messages have roles: `system`, `user` and `assistant`.
- A `system` message sets the rules.
- To continue a conversation, send all of it.
- Streaming gives you the reply piece by piece.

## Where this comes from

Ollama's chat format follows the messages style that's now common across model providers. To learn
more, see the [Ollama API documentation](https://docs.ollama.com/api).

**Next:** chapter 07, where you'll find out why those two puzzles happened.
