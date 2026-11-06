# Chapter 24: Context management

**Time:** about 2 hours. The long test is optional. **You'll build:** a token budget for a long chat, a
warning for the silent cut, and two ways to stay inside the budget. Then you'll measure what each one loses.

## Where we are

Part 4 ended with an agent that could search. Every run so far has been short: one question, a few
messages, and an answer. Real assistants don't work like that. A person keeps talking, and every old
message goes back to the model on every turn.

You've seen what happens to text that doesn't fit. In chapter 20, a pasted handbook was silently cut, and
only `tokens_in` gave it away. This chapter is the same problem in a chat, where it's harder to spot,
because the cut takes the oldest messages and everything else still looks fine.

This is the first chapter of Part 5, and the part has one thread: **let the model make the judgement
call, and keep the facts, the order and the truth in code.** This chapter shows why.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in chapter 05.
You'll work in `chapters/24-context-management/code`.

One file is new in the framework: `whitebox/context.py`. `agent.py` doesn't change. Everything here plugs
into chapter 16's hooks, or into the `history` argument of `agent.run`. These things are provided, and you
don't need to change them:

- `staff_chat.py` builds the long chats. A person called Priya tells the assistant a few facts, then asks
  about the handbook. The handbook answers are the first 130 words of a handbook file, so every run
  has the same chat. It has three chats, explained as you meet them.
- `results/` holds our saved long test. `long_scores.py`, `long_note.py` and `long_answers.py` read it, and
  they use your own files if you've made them. So **you can follow the whole chapter without the long test.**
- `library.py`, `questions.py` and `make_records.py` are from Part 4. We only use `OPTIONS` and `saved` here.
- `find_cut.py`, `short_test.py` and `long_test.py` are measuring scripts. Each section says what the script does
  and shows the part that matters.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `69 passed`. These tests use a fake model, so they don't need Ollama.

## 1. A chat that forgets

Open [code/long_chat.py](code/long_chat.py). It asks for Priya's staff number straight after she gives
it, and again after 40 handbook questions:

```python
for handbook_turns in (0, 40):
    messages = staff_chat(handbook_turns) + [Message("user", QUESTION)]
    reply = model.chat(messages, **OPTIONS)
    print(f"After {handbook_turns + 3} turns, {len(messages)} messages sent")
    print(f"  tokens_in: {reply.tokens_in}")
    print(f"  Answer: {reply.content}")
```

The whole chat goes to the model each time, and "My staff number is 4471." is in both lists.

**Predict:** will it find the number both times?

```bash
python3 long_chat.py
```

This is real output from `qwen2.5:7b`:

```text
After 3 turns, 8 messages sent
  tokens_in: 134
  Answer: Your staff number is 4471. Cheers
After 43 turns, 88 messages sent
  tokens_in: 4021
  Answer: I'm here to assist with your questions about the handbook and Quillon Coffee policies, but I don't have access to personal information like your staff number. If you need to find your staff number, you can check your employee profile in StaffHub or contact your branch manager for assistance. Cheers
```

No error and no warning. We sent 88 messages, the number was in them, and the assistant says it can't
know it. It doesn't sound confused either. It doesn't know it ever knew.

## 2. Count what you send

You can't manage what you don't measure. Ollama only tells you `tokens_in` after the call, so you need
your own count before it. Here's the start of [code/whitebox/context.py](code/whitebox/context.py):

```python
def estimate_tokens(message):
    """A rough count: about four characters for each token, plus a little for the message itself."""
    return len(message.content) // 4 + 4


def total_tokens(messages):
    return sum(estimate_tokens(message) for message in messages)
```

Four characters a token is a rule of thumb, and it's free: no model call, no tokenizer. How rough is it?
[code/count_chat.py](code/count_chat.py) compares it with the model's own count, in a window big enough
that nothing is cut:

```python
# One token of reply, because we only want the count.
estimate = total_tokens(messages)
real = model.chat(messages, num_ctx=16384, num_predict=1).tokens_in
```

```bash
python3 count_chat.py
```

```text
Turns  Messages  Estimate   Real  Off by
    3         8       113    134    -16%
    8        18       797    792      1%
   23        48     2,754  2,754      0%
   43        88     5,317  5,294      0%
   83       168    10,578 10,460      1%
```

Within 1% on the long chats, which are what matter here. It's 16% low on a tiny chat, where the model's
own wrapping around each message counts for more. That's on English prose, with this model's tokenizer.
Code or other languages would differ, so treat it as a rough count, and check it the same way.

## 3. Find the cut

Now you have two numbers: what you **sent**, by `total_tokens`, and what the model **read**, in `tokens_in`.
[code/find_cut.py](code/find_cut.py) grows the chat, and asks for each of three facts five times at each
length. The system message says to end every reply with "Cheers", so the last column shows whether it survived:

```python
for _, question, word in QUESTIONS:
    passed = 0
    for _ in range(RUNS):
        reply = model.chat(chat + [Message("user", question)], **options)
        right = word in reply.content.lower()
        passed += right
        rule += "cheers" in reply.content.lower()
```

The last row repeats the longest chat with `num_ctx` 16384. `model` here is `Retry(load_model())`, from
chapter 17, so a slow reply doesn't end a long test. **Predict:** does recall fade slowly, or fall off a cliff?

```bash
python3 find_cut.py
```

The script cuts answers at 110 characters:

```text
Window   Turns   Sent   Read  Name  Number  Day   Cheers
default      3    104    135     5       5    5    15/15
default      8    788    793     5       5    5    15/15
default     13  1,394  1,435     5       5    5    15/15
default     23  2,745  2,755     5       5    5    15/15
default     43  5,308  4,022     0       0    0    15/15
16384       43  5,308  5,295     5       5    5    15/15

15 wrong answers: 11 said they didn't know or couldn't say, 4 didn't
 - I don't have your name on file, but you can call me Quillon Coffee Assistant. How can I assist you further? Ch
 - I don't have your name on file, but you can call me Quillon Coffee Assistant. How can I assist you further? Ch
 - I'm sorry, but I don't have access to your personal information or staff number. You can find your staff numbe
 - Your name isn't provided in the context of our conversation. How can I assist you further, [Your Name]? Cheers
 - Your name is not provided in the context, but if you need any assistance or have specific questions related to
 - Your name isn't mentioned in the handbook, but I'm here to assist you with any questions about the Quillon Cof
```

Read the table:

- **It's a cliff.** Recall was perfect at 2,755 tokens, and 0 of 15 at 4,022. We didn't test the lengths in between.
- **Sent and Read match, until they don't.** At 43 turns we sent about 5,300, and the model read about 4,000.
  That's the window from chapter 20, 4,096 on our machine. Yours may differ, so trust `tokens_in`.
- **The same chat scored 15 of 15 at `num_ctx` 16384.** The facts weren't too hard. They were gone.
- **"Cheers" survived every time.** In chapter 20, the rules were the first thing lost. Here they weren't.

That last point needs a word. In chapter 20, everything was in one big message, and `tokens_in` stopped at
2,050. A chat is a list of messages, and our results point to a different cut: the system message stays,
and the oldest whole messages go. So the assistant keeps its manners and loses its memory, which is why
it's so easy to miss.

The bottom lines are the failures. Our word list counted 11 of the 15 as refusals, and the others printed here say
the same thing in other words. None of the answers printed invents a fact. As far as the model can tell, Priya
never said anything.

## 4. Make the cut loud

The first fix is to stop the silence. `CutWarning` is a hook, like chapter 16's `Tracer`. It uses two of the
moments you know:

```python
class CutWarning(Hook):
    """Warn when the model read far fewer tokens than we sent, because the provider cut them silently."""

    def before_model(self, messages):
        self.sent = total_tokens(messages)

    def after_model(self, reply):
        if reply.tokens_in and reply.tokens_in < self.sent * 0.9:
            warnings.warn(f"Sent about {self.sent} tokens, but the model read {reply.tokens_in}.")
```

- `warnings` is part of Python. `warnings.warn` prints a message to the error stream and carries on, so
  the run isn't stopped.
- The 0.9 leaves room for the estimate to be rough. Section 2 showed it's close on this kind of text.
- `reply.tokens_in and` skips a model that reports no count, because 0 would look like a cut.
- `flush=True`, in the script below, prints at once, so the output stays in order with the warning.

[code/warn_cut.py](code/warn_cut.py) runs the 43-turn chat through an `Agent`, using `history`. You met
`agent.run` in chapter 15. Pass it a list of messages as `history`, and the run carries on from there:

```python
for label, options in (("Default window", OPTIONS), ("num_ctx 16384", {**OPTIONS, "num_ctx": 16384})):
    print(label, flush=True)
    agent = Agent(model, options=options, hooks=[CutWarning()])
    result = agent.run(QUESTION, history=staff_chat(40))
    print("  Answer:", result.answer, flush=True)
```

```bash
python3 warn_cut.py
```

We've shortened the file path in the warning, which is the only change here:

```text
Default window
whitebox/context.py:43: UserWarning: Sent about 5317 tokens, but the model read 4021.
  warnings.warn(f"Sent about {self.sent} tokens, but the model read {reply.tokens_in}.")
  Answer: I'm here to assist with information from the handbook and provide guidance, but I don't have access to personal information like your staff number. If you need to find your staff number, you can check your staff card or log in to StaffHub. If you're unsure and need to contact someone for assistance, you can reach out to your branch manager or Tomas Weir. Cheers!
num_ctx 16384
  Answer: Your staff number is 4471. If you need any more information or assistance, feel free to ask! Cheers
```

It spoke up on the real cut, and stayed quiet when nothing was cut. Add it to any agent that holds a long
chat. It doesn't fix anything, but you'll never again wonder why an assistant went blank.

## 5. Trim

If something must go, you can choose what, rather than leave it to the provider. That's a **token budget**:
a number you pick, below the window, that the chat must stay under.

`newest` walks back from the end, and keeps messages until the budget is spent:

```python
def newest(messages, budget):
    """Return the newest messages that fit the budget, oldest first."""
    kept, used = [], 0
    for message in reversed(messages):
        used += estimate_tokens(message)
        if used > budget:
            break
        kept.insert(0, message)
    while kept and kept[0].role == "tool":
        kept.pop(0)  # A tool result makes no sense without the call that asked for it.
    return kept
```

`insert(0, message)` puts it at the front, so the list ends up oldest first. The `while` loop matters in an
agent, because a tool result makes no sense if the call that asked for it was trimmed away.

`Trim` is a hook that uses it before each model call:

```python
class Trim(Hook):
    """Before each model call, keep the system message and the newest messages that fit."""

    def __init__(self, budget):
        self.budget = budget

    def before_model(self, messages):
        if total_tokens(messages) > self.budget:
            system, rest = messages[:1], messages[1:]
            messages[:] = system + newest(rest, self.budget - total_tokens(system))
```

`messages[:] = ...` replaces what's inside the list, rather than making a new list. It has to, because the
agent's loop holds this same list. `messages = ...` would only change the hook's own name for it, and the
agent wouldn't see any change. Trimming also pins the system message, so the rules stay on purpose, not by luck.

[code/trim_chat.py](code/trim_chat.py) trims the same chat to 3,000 tokens, and looks at what's left:

```python
messages = staff_chat(40) + [Message("user", QUESTION)]
print(f"Before: {len(messages)} messages, about {total_tokens(messages):,} tokens")

Trim(BUDGET).before_model(messages)
print(f"After:  {len(messages)} messages, about {total_tokens(messages):,} tokens")
```

The rest of the script prints the first two messages, then asks an `Agent` that has `hooks=[Trim(BUDGET)]`.

**Predict:** will it find the staff number now?

```bash
python3 trim_chat.py
```

```text
Before: 88 messages, about 5,317 tokens
After:  47 messages, about 2,993 tokens
First: You are the Quillon Coffee staff assistant. End every reply 
Then:  # First aid Every branch has a first aid kit behind the coun
tokens_in: 2970
Answer: I'm here to assist with information from the handbook and FAQs, but I don't have access to personal employee details like your staff number. You can find your staff number on your employee record or payslip. If you need assistance locating it, feel free to ask! Cheers
```

The budget held. The number is still gone, because it's old, and old is what you told `Trim` to remove.
So `Trim` doesn't remember more than the silent cut. What you get is control: you know what goes and when,
the rules are safe, and you're sending about 3,000 tokens and not 5,300.

Look at the `Then:` line too. The first message after the system message is a handbook answer, with its
question trimmed away. `newest` only protects against a lone tool result. Exercise 3 fixes that.

## 6. Summarise

So don't throw the old messages away. Ask the model to shrink them:

```python
SUMMARY = (
    "Summarise this conversation for an assistant taking over. Keep every personal fact the user gave, such as "
    "names, numbers and days, exactly. Leave out handbook text.\n\n{text}"
)
```

```python
class Summarise(Hook):
    """Before each model call, fold the older messages into one note the model rewrites each round."""

    def __init__(self, model, budget, options=None):
        self.model = model
        self.budget = budget
        self.options = options or {}

    def before_model(self, messages):
        if total_tokens(messages) <= self.budget:
            return
        keep = newest(messages[1:], self.budget // 2)
        older = messages[1:len(messages) - len(keep)]
        system, _, note = messages[0].content.partition(NOTE)
        text = f"Earlier notes: {note}\n" if note else ""
        text += "\n".join(f"{message.role}: {message.content}" for message in older)
        reply = self.model.chat([Message("user", SUMMARY.format(text=text))], **self.options)
        messages[:] = [Message("system", system + NOTE + reply.content)] + keep
```

Half the budget keeps the newest messages word for word. Everything older goes to the model, and the
summary joins the system message, after a line called `NOTE`: "Earlier in this conversation:". If there's
already a note, it goes in with the older messages, and one new note comes out, so there's only ever one.

`partition(NOTE)` splits a string around the first `NOTE`, and gives back three parts: before, `NOTE`, and
after. So `system` is the original rules, and `note` is the old note, or an empty string if there isn't one yet.
`options` is there because the summary call needs its own window: the
text being summarised has to fit too. We use `{"temperature": 0.2, "num_ctx": 8192}`, with a low temperature
because we want a careful note, not a varied one.

[code/summary_chat.py](code/summary_chat.py) uses the second chat in `staff_chat.py`. It has 45 turns and
five facts: three at the start, a manager near the middle, and a shift time in the last turn. The script
summarises once, prints the first 500 characters of the note, and asks for all five:

```python
Summarise(model, BUDGET, FOR_SUMMARY).before_model(messages)
print(f"After:  {len(messages)} messages, about {total_tokens(messages):,} tokens")
```

```bash
python3 summary_chat.py
```

```text
Before: 91 messages, about 5,355 tokens
After:  25 messages, about 2,670 tokens
The note:
Hello Priya,

You work at the Harbour branch with staff number 4471. You can't work on Tuesdays due to your college course. Here are some key points from the handbook:

- **Accidents and Incidents**: Report any injury or near miss on form IR-7 before the end of the shift. Branch manager sends it to Ines Duarte within 24 hours.
- **Allergens**: Handle milk, soya, nuts, gluten, egg, and sesame. Always check the allergen folder and use clean utensils. Almond croissant and seeded flapjack are high-r

pass  What's my name?  Your name is Priya. How can I assist you further with your s
pass  What's my staff number?  Your staff number is 4471. Cheers
pass  Which day can't I work?  According to your information, you can't work on Tuesdays du
pass  What's my manager called?  Your manager is Tomasz. Cheers
pass  What time does my shift start tomorrow?  Your shift starts at 06:30 tomorrow. Remember to arrive 10 m
```

All five. Under budget, and the staff number is back. Notice one thing, though. We said "Leave out handbook
text", and the note went straight on to "key points from the handbook". Remember that.

## 7. The short test

One run proves little. [code/short_test.py](code/short_test.py) tries four setups on that 45-turn chat, five
runs each, so each fact is asked 5 times per setup:

```python
if label == "nothing":
    return chat, Agent(model, options=OPTIONS)
if label == "window 16384":
    return chat, Agent(model, options={**OPTIONS, "num_ctx": 16384})
if label == "Trim":
    return chat, Agent(model, options=OPTIONS, hooks=[Trim(BUDGET)])
Summarise(model, BUDGET, FOR_SUMMARY).before_model(chat)  # Once per run, then every question uses the note.
return chat, Agent(model, options=OPTIONS)
```

**Predict:** which ones get all 25?

```bash
python3 short_test.py
```

```text
Setup              name   number      day  manager    shift   Total   Read
nothing               0        0        0        5        5   10/25  4,084
window 16384          5        5        5        5        5   25/25  5,357
Trim                  0        0        0        5        5   10/25  2,922
Summarise             5        5        5        5        5   25/25  2,996
```

`Read` is the last call's `tokens_in`.

- **Nothing and `Trim` tie at 10.** Both lose the three oldest facts. They keep the newer two.
- **The bigger window and `Summarise` both score 25.** `Summarise` read about 3,000 tokens, against about 5,400.

If you stopped here, you'd ship `Summarise`. It's perfect, it's smaller, and it has passing tests. But
look at what this test is: one summary, of one chat, with five easy facts. A real chat doesn't stop at 45 turns.

## 8. The long test

The third chat in `staff_chat.py` has 120 turns, about 14,400 tokens, with twelve facts spread evenly
through it. A chat that long passes the budget again and again, so it's summarised again and again.

[code/long_test.py](code/long_test.py) plays the chat one turn at a time, and runs the hook before each
reply, just as it would inside an `Agent`. The replies come from the script, so every run has the same chat:

```python
def play(hook):
    """Play the chat one turn at a time. The hook runs before each reply, as it would inside an Agent."""
    messages, rounds = [Message("system", SYSTEM)], 0
    for question, answer in long_turns():
        messages.append(Message("user", question))
        before = messages[0].content
        hook.before_model(messages)
        rounds += messages[0].content != before
        messages.append(Message("assistant", answer))
    return messages, rounds
```

At the end it asks for all twelve facts, at the default window, three times over. That's 36 questions.
The word checks are the same kind as before, and each answer is saved so you can read it. For comparison,
the `window` setup sends the whole chat at `num_ctx` 24576, so nothing is cut.

**Predict:** the budget is 3,000. Will it hold? And how many of the 36 come back?

That's about 80 model calls for `summarise`, and 36 long ones for `window`, so you don't have to run them. If you want to:

```bash
python3 long_test.py summarise
python3 long_test.py window
```

Our runs are saved, and this prints them, with no model:

```bash
python3 long_scores.py sizes
```

```text
Setup      Run  Right  Summaries    Sent    Read  Cheers
window       1      6          0  14,409  14,320   12/12
window       2      9          0  14,409  14,320   12/12
window       3      7          0  14,409  14,320   12/12
summarise    1      2         12   3,079   3,125   12/12
summarise    2      1         14   2,682   2,787   12/12
summarise    3      2         14   2,935   2,985   12/12
```

`Summarise` did its job. It took 12 to 14 summaries, `Read` matches `Sent`, and "Cheers" came back every time.
The budget held, near enough: the check runs before each reply, so the last reply can land just over it.

And the score is 1 or 2 of 12. Here's why, fact by fact. `In note` counts the runs whose final note holds the
person's own fact:

```bash
python3 long_scores.py
```

```text
Right answers, and final notes that hold the fact, out of 3 runs
Fact       Window  Summarise  In note
name            0          0        0
number          1          0        0
day             0          0        0
locker          3          0        0
allergy         2          0        0
manager         3          0        0
bus             2          0        0
size            1          0        0
till            1          0        0
sister          3          0        0
course          3          2        2
shift           3          3        0
Total          22          5        2   (of 36)
```

5 of 36. The notes held a personal fact only 2 times in 36. `course` is in two notes, and it came back those
two times. `shift` scored 3 of 3 without being in any note: it's so recent that it's still in the chat word for
word. The other ten facts are gone. Each round is a new chance to drop a fact, and a fact that's dropped once
can't come back.

So what's in the notes? `python3 long_note.py` shows the start of each one:

```text
Run 1: one note, about 805 tokens
  Starts: # Summary of Key Information  - **Uniform**: Staff must wear a white t-shirt with the Quillon logo, black trousers or a black skirt, and black shoes. 
Run 2: one note, about 784 tokens
  Starts: # Accidents and incidents - Any injury, even minor, must be reported on form IR-7 before the end of the shift. - Branch managers send the form to Ines
Run 3: one note, about 1,183 tokens
  Starts: # Summary of Key Information from the Handbook for Branches  ## Old Mill Branch - **Address**: The Old Mill, Weir Lane. - **Manager**: Ravi Nair. - **
```

We said "Leave out handbook text". Each note is a tidy handbook summary. That's what you saw in section 6, and
each round did it again. A personal fact is one short line among long, important-looking rules, and the model
keeps what looks important.

Most of the failures are polite, like the cut. Not all. `python3 long_answers.py manager` prints every answer
for one fact, cut at 120 characters:

```text
window     pass  Your manager is called Tomasz. Cheers
window     pass  Your manager is called Tomasz. Cheers
window     pass  Your manager is called Tomasz. Cheers
summarise  FAIL  Your manager is Lena Ortiz at the Harbour branch. If you work at a different branch, please let me know which one, and I
summarise  FAIL  Your manager is Lena Ortiz at the Harbour branch. If you're at a different branch, please specify, and I'll provide the 
summarise  FAIL  Your manager is Mei Tanaka for the Station Branch. If you have any questions or need assistance, feel free to reach out 
```

Priya's manager is Tomasz. Lena Ortiz and Mei Tanaka are real names too, from the handbook, because that's what
the note held. So the model answered from the note, confidently, in 3 runs of 3. A blank is bad. A believable
wrong name is worse.

## 9. A bigger window isn't the fix

So why not just raise `num_ctx`? It scored 25 of 25 on the short test. The whole 120-turn chat fits at 24,576:
`Read` is 14,320, and nothing is cut. Every fact is right there. Look at `Window` in the table: 22 of 36.

Read those passes too. `python3 long_answers.py allergy`:

```text
window     pass  It seems like you might be referring to an allergy, but you didn't specify what you're allergic to. If you need informat
window     pass  It seems like you're asking about allergies, but I don't have specific information about your allergies from the handboo
window     FAIL  To ensure your safety, could you please specify what you are allergic to, such as specific foods or substances? This inf
summarise  FAIL  The handbook states that staff are handled milk, soya, nuts, gluten, egg, and sesame on site. Always check the allergen 
summarise  FAIL  The handbook doesn't list individual allergies; instead, it advises that all staff should handle milk, soya, nuts, glute
summarise  FAIL  According to the handbook, you should handle milk, soya, nuts, gluten, egg, and sesame. However, you can never promise a
```

Both window passes are false. The model says it doesn't know the allergy, and then uses cashews as an example,
because the word is in front of it. So the window got 20 of 36 by our reading. Runs went from 6 to 9 of 12 by the
word check.

That's a little over half, with every fact in the window. Read the column: `locker`, `manager`, `sister`, `course`
and `shift` came back every time. `name` and `day`, two of the three oldest facts, never did. The answers sound just
like the cut did:

```text
window     FAIL  I don't have access to your personal information, so I don't know your surname. How can I assist you with the handbook i
window     FAIL  I don't have your specific information on file, but you mentioned your sister's name is Anjali. If you're asking about y
window     FAIL  To better assist you, could you please specify which day you are unable to work or provide more details about your sched
window     FAIL  Noted. To help you better, could you please specify which day you mentioned or provide more details about your availabil
```

**Fitting isn't the same as being used.** Those facts were read, and among 14,000 tokens of handbook text the
model didn't find them. A bigger window also sends more tokens on every turn, and it's only a further cliff:
a longer chat would reach it.

Here's what the numbers can and can't support:

| Claim | Our evidence |
|---|---|
| On this chat, repeated summaries lost most facts | 5 of 36, and 2 notes of 36 held a personal fact |
| A bigger window recalled a little over half | 22 of 36 by the word check, 20 by reading the answers |
| A summary can pass a short test and fail a long one | 25 of 25, against 5 of 36 |
| A bigger window beats summaries in general | **Not shown.** It did on this chat, at about five times the tokens on every turn, and it still lost a good part of the facts |

Three more limits. This is one chat, built by us, with scripted replies, and three runs of each setup. The word
checks need reading, as you've seen. And we tested one 7B model. A bigger model may well write a better note and
find a fact in a long window, so don't read this as a law. Run `long_test.py` on your own model, then read the answers.

| Your situation | What to try |
|---|---|
| Any long chat | `CutWarning`, always. It costs nothing |
| Old messages don't matter | `Trim`. It's simple, and it's honest about what it loses |
| A chat that passes the budget once or twice | `Summarise`, with the note read and tested |
| Everything fits in the window | A bigger `num_ctx`, and measure recall, not just fit |
| Facts must survive a long chat | Nothing in this chapter. That's the next one |

## Reading errors

We triggered each of these for real.

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| A reply took too long, on a busy machine | `Read timed out. (read timeout=180)` | Wrap the model in `Retry`, or run less at once |
| You ran `long_test.py` or `long_answers.py` with no word | `IndexError: list index out of range` | Add one: `python3 long_test.py summarise` |
| You named a setup that doesn't exist | `KeyError: 'summary'` | Use `window` or `summarise` |
| You named a fact that doesn't exist | `StopIteration` | Use a name from `FACTS` in `staff_chat.py` |
| The chat was cut | `UserWarning: Sent about 5317 tokens, but the model read 4021.` | It's `CutWarning` working. Trim, summarise or raise `num_ctx` |
| The chat was cut, with no `CutWarning` | No error at all. The assistant says it doesn't have the information | Compare `total_tokens` with `tokens_in` |

## Exercises

From `chapters/24-context-management`, open [exercises.py](exercises.py) and complete the five TODOs:

1. `tokens_lost`: how many tokens the provider cut, from what you sent and what the model read.
2. `still_has`: check whether a fact is still in the chat after a trim.
3. `newest_turns`: `newest`, but it never starts on an assistant reply, as `Trim` did in section 5.
4. `CountingTrim`: a `Trim` that adds up how many messages it removed.
5. `missed`: ask for each fact, and return the names of the ones the agent got wrong.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find the `whitebox` package
inside `code/`. Exercise 4 uses `super()`, which is new. Inside a class, it reaches the parent class, so `super().before_model(messages)`
runs `Trim`'s own version, and `super().__init__(budget)` runs its setup. You add to them rather than copy them.

Then check your work from `chapters/24-context-management`. These checks use a fake model, so Ollama doesn't
need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

**Exercise 6, optional: write a better summary.** `Summarise` reads its prompt from `SUMMARY` in
`whitebox/context.py`. Change it, keeping `{text}` in it, then run `python3 long_test.py summarise` and
`python3 long_scores.py`. Watch the `In note` column, and read the note with `python3 long_note.py`. There's no
worked answer, because we don't have one. Wording matters a lot here, so change one thing at a time.

## Common mistakes

- **Trusting a chat because there was no error.** The cut raised nothing. Compare `total_tokens` with `tokens_in`.
- **Testing only a short chat.** `Summarise` scored 25 of 25 once, and 5 of 36 on a long chat.
- **Trusting a note you haven't read.** We said "Leave out handbook text", and the notes were handbook text.
- **Reading a sure answer as a right one.** "Your manager is Lena Ortiz" sounded just as sure as Tomasz.
- **Believing a pass you haven't read.** "If you're allergic to cashews" isn't knowing Priya's allergy.
- **Thinking `Trim` remembers.** It chooses what to lose. It still loses it.
- **Reaching for a bigger window.** It fits the text. It doesn't make the model use it.

## Recap

- A long chat loses its oldest messages with no error. The system message stayed, and the facts went: 15 of 15
  at 2,755 tokens, and 0 of 15 at 4,022. The assistant doesn't know it ever knew.
- `estimate_tokens` and `total_tokens` give a free, rough count, within 1% on these long chats.
- `CutWarning` compares what you sent with what the model read, and speaks up.
- A token budget lets you choose. `Trim` keeps the newest messages. `Summarise` asks the model for a note.
- One summary on a 45-turn chat scored 25 of 25, level with a bigger window.
- Over 120 turns, repeated summaries held the budget and scored 5 of 36. The notes were mostly handbook text.
- A bigger window fit the whole chat, and recalled 20 to 22 of 36.

**Summaries lose the facts that matter.** The model decides what looks important, and a staff number never does.

## Where this comes from

Long inputs not being used evenly was measured in the 2023 paper
[Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172). Its pattern isn't
quite ours: it found the middle did worst, and here some of the oldest facts did. So measure your own.

**Next:** chapter 25, memory, keeps those facts in code.
