# Chapter 25: Memory

**Time:** about 2 hours. The long runs are optional. **You'll build:** notes on disk that outlive a
session. The model says when to save, and your code keeps the user's own words, in order.

## Where we are

Chapter 24 kept a long chat inside its token budget, and it ended on a warning: summaries lose the
facts that matter. That was one long conversation. This chapter has a harder problem. The conversation
ends. The program stops, the messages are gone, and the next session starts from nothing.

So you need something that isn't the conversation at all. By the end of this chapter, you'll have
`Memory`, a small class that keeps notes in a JSON file. Along the way you'll settle three questions: who
decides what's worth saving, whose words get saved, and what happens when a saved fact stops being true.

Chapter 24 gave you the thread for this part: **let the model make the judgement call, and keep the
facts, the order and the truth in code.** This chapter is where the facts and the order go into code.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. You'll work in `chapters/25-memory/code`.

One file is new in the framework: `whitebox/memory.py`. Section 7 reads all of it. These things are
provided, and you don't need to change them:

- `hana.py` holds the person this chapter follows. Hana Kowalski is made up for this chapter. It has her
  12 facts, the 24 other things she says, and the small helpers that every script shares: `chat`,
  `with_notes`, `recall`, `right` and `about_hana`. Each is a few lines, so have a read.
- `results/` holds our saved runs. A script that reads results uses your own file if you've made one, and
  ours if you haven't. So **you can follow the whole chapter without the long runs.** Notes files you make yourself stay out
  of git, because this chapter's `.gitignore` has `code/*.json`.
- `who_decides.py`, `whole_chat.py`, `wording.py` and `stale_notes.py` are measuring scripts, and
  `read_notes.py` reads what they saved. Each section says what the script does and shows the part that
  matters.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `74 passed`. These tests use a fake model, so they don't need Ollama.

## 1. A new session

Open [code/forgot.py](code/forgot.py). Hana tells the agent three things, one message at a time. Each message
goes in with the history so far, as you've done since chapter 15. Then the script asks for her locker number
twice:

```python
history = told_it()
print("Same session:", agent.run(QUESTION, history).answer)
print("New session: ", agent.run(QUESTION).answer)
```

The only difference is `history`. A new session is the same agent, with nothing passed in. It's what you get
when someone closes the app and comes back tomorrow. **Predict:** what will the second line say?

```bash
python3 forgot.py
```

This is real output from `qwen2.5:7b`, with the long second answer cut at 150 characters by us:

```text
Same session: Your locker number is 212, Hana. If you need any help with it or have any other questions, feel free to ask!
New session:  I'm sorry, but I don't have any information about your locker number. Could you provide more context or details about where this locker 
Over 5 runs: same session 5/5, new session 0/5
```

There's no error, and nothing is cut. The model isn't being careless, either. It never had the number. Everything
an agent knows about a person lives in `messages`, and `messages` is a Python list that disappears with the run.

Chapter 24's tools can't help. `Trim` and `Summarise` manage a conversation that's still going. This one's over.
Something has to be written down outside it.

## 2. Write it down at the end

The obvious plan: when the chat's over, hand it to the model and ask for the facts. That's
[code/all_at_once.py](code/all_at_once.py). From here on, every script uses Hana's full chat, from `hana.py`: 36
messages, with 12 facts about her among 24 other things. Some facts are plain, such as "My staff number is 5093."
Others are tucked behind a question: "What's the rule on sick pay? I've got a bad knee so I might need it." And some
of the other messages sound like facts, but aren't about her: "Marek on the next till is off with flu."

The script sends 12 messages at a time, so the chat takes three blocks:

```python
reply = model.chat([Message("user", EXTRACT.format(text="\n".join(block)))], temperature=0.2).content
```

```bash
python3 all_at_once.py
```

```text
round 1: 14 lines, 10 of 12 facts
round 2: 14 lines, 10 of 12 facts
round 3: 13 lines, 10 of 12 facts
round 4: 13 lines, 10 of 12 facts
round 5: 13 lines, 10 of 12 facts
NONE in 0 of 15 blocks
One round's lines:
  - Hana Kowalski
  - Staff number is 5093
  - Locker number is 212
  - Can't do Thursdays, has a night class in bookkeeping
  - Oat milk delivery came two hours late today
  - NONE
  - Emergency contact is my brother Piotr.
  - Can carry leave over and save days for a trip to Lisbon in October.
  - Been on the 06:15 opener rota since Monday
  - My badge says Johanna but everyone calls me Hana
  - Marek on the next till is off with flu
  - I get the number 18 bus in, so Sundays are tight for me
  - My food hygiene certificate runs out on 9 November
```

Ten of 12 isn't bad. In our earlier testing, on a different chat, the model replied `NONE` to most blocks. This
chapter didn't reproduce that, so treat both as single results, and read the lines:

- **The bad knee and the hazelnut allergy are gone.** Both came after a question. "Allergic to hazelnuts" is the
  one fact here that could hurt her. Every round found 10, and these are the two missing from the lines shown.
- **Some lines aren't about her.** The late oat milk and Marek's flu are in there as facts about Hana.
- **One line changed the meaning.** She asked "Can I carry leave over?" and the note says she "Can carry leave
  over". A question became a rule. It would read just as confidently next month.

And there's a problem no score shows. This only runs if the session ends cleanly. If the program dies, nothing's
saved. It'd be better to decide message by message, as the chat goes. So who should decide?

## 3. Who decides?

[code/who_decides.py](code/who_decides.py) tries three answers. All three see the same 36 messages, one at a time. Each
message is its own run with no history, so each decision is about that one message. Then `recall`, from `hana.py`, asks
the 12 questions, each in a new session with only the notes.

**Code checks.** Your code asks about every message, with a fixed prompt, and saves the message if the answer has a
fact in it. A model still reads each message, but it can't skip one. This is `CHECK`, in `rewritten.py`:

```text
Does this one message state a fact about the person writing it? If yes, reply with the fact on one line
starting with '- ', copying names, numbers, dates and times exactly. A question is not a fact. If no, reply NONE.
```

**The model's words.** The agent gets a `remember` tool, and saves whatever it writes:

```python
@tool
def remember(fact: Annotated[str, "The fact to keep, in a short sentence"]) -> str:
    """Save something about the user for future conversations."""
    notes.append(fact)
    return "Saved."
```

**The user's words.** The same tool, and the same choice about when to call it. But the code ignores what the model
wrote, and saves the message:

```python
if said["latest"] not in notes:
    notes.append(said["latest"])
```

`said` is a dictionary, so the tool can see a change made outside it. **Predict:** which setup will remember most? And
which will save the most rubbish?

The full run is about 900 model calls, so you don't have to do it. To see one setup work, run
`python3 who_decides.py "code checks"`. That's about 240 calls. It writes `who-decides.json`, and
[code/read_notes.py](code/read_notes.py) reads your file if there is one, and ours if not:

```bash
python3 read_notes.py
```

```text
Setup            Recall     Notes  Unwanted  Her words
code checks       39/60    8 to 8    0 to 0      40/40
model's words     50/60  14 to 18    3 to 6      21/77
user's words      59/60  15 to 18    3 to 6      85/85
Memory            57/60  13 to 15    2 to 3      69/69

Missed, out of 5 runs each:
code checks     knee 5, allergy 5, trip 5, badge 5, hygiene 1
model's words   knee 3, trip 2, badge 5
user's words    knee 1
Memory          knee 3
```

`Recall` is right answers in a new session. `Notes` and `Unwanted` are ranges across the five runs, and an unwanted note
is one that holds none of the 12 facts. `Her words` counts notes that are exactly something she said. Ignore the
`Memory` row for now. Section 9 explains it.

- **Code checks saved nothing unwanted, and missed the most.** It never once kept the knee, the allergy, the trip or the
  badge. Three of those come after a question, and `CHECK` says a question isn't a fact.
- **The two tool setups remembered more, and saved rubbish.** Three to six unwanted notes a run.
- **Keeping her words scored 59 against 50 here.** That's a real gap on this chat, and the `Missed` lines show where it
  came from: the badge, 5 times out of 5, then the knee and the trip. The next two sections look at why. It's one chat, so treat the gap
  as something to explain, not as a ranking.

## 4. Read the notes

The score doesn't tell you what's in the file, so read it. Name a setup, and `read_notes.py` lists its unwanted notes:

```bash
python3 read_notes.py "model's words"
```

```text
Unwanted notes in model's words, with how many runs saved each:
4  A blue scarf was left on table 4.
4  Harbour was packed when I dropped in earlier.
1  Harbour was packed when the user dropped in earlier.
4  Marek is off with flu.
1  Marek is off with the flu.
1  The flapjack contains nuts.
1  The oat milk delivery arrived two hours late today.
4  The oat milk delivery was two hours late today.
1  The user asked about logging waste.
1  The user asked about the staff discount on bags of beans.
```

Most are ordinary noise. Look at two of them. "The flapjack contains nuts." Hana *asked* whether it did: "Someone asked if
the flapjack has nuts in it." The model turned her question into an allergen fact. It only happened in 1 run of 5, but
in a coffee shop that's the worst note in the list, and a later session would treat it as something she said.

The other isn't in that list, because it counts as being about her: "Johanna is known as Hana." She said "My badge says
Johanna but everyone calls me Hana." The model saved that in all 5 runs, and dropped the word "badge". So all 5 runs
failed "What name is on my badge?". That's the 5 in the `Missed` line.

The user's-words setup can't do either of these. It saved unwanted notes too, as many as the model did. But each one is
something she really said. **The difference between the two isn't how much they save. It's that one can invent, and the
other can't.**

## 5. The bare 212

"The flapjack contains nuts" is easy to spot once you read it. Here's a quieter way for rewritten notes to go wrong.
[code/rewritten.py](code/rewritten.py) checks every message with the same `CHECK` prompt, but saves the
model's line, not Hana's message:

```python
for text in chat():
    reply = model.chat([Message("user", CHECK.format(text=text))], temperature=0.2).content
    notes += [line[2:].strip() for line in reply.splitlines() if line.startswith("- ")]
answers = recall(model, with_notes(notes))
```

`CHECK` tells the model to copy names, numbers, dates and times exactly. It does. **Predict:** what could go
wrong with a note that copies a number exactly?

```bash
python3 rewritten.py
```

```text
run 1: 6 of 12. Locker: Your locker number is 5093.
run 2: 6 of 12. Locker: Your locker number is 5093.
run 3: 5 of 12. Locker: Your locker number is 5093.
run 4: 6 of 12. Locker: Your locker number is 5093.
run 5: 5 of 12. Locker: Your locker number is 5093.
Notes from the last run:
  - Hana Kowalski
  - 5093
  - 212
  - Thursdays
  - Piotr
  - 06:15
  - Monday
  - 18
  - 9 November
```

Every value is exact, and almost every note is useless. `212` is right there, with nothing to say it's a
locker. `5093` is her staff number, and it's the one the model picked: "Your locker number is 5093", in all 5
runs, with no doubt in the wording.

The other notes do damage too. `Thursdays` has lost whether she can or can't work them. `Monday` came from
"Been on the 06:15 opener rota since Monday", and one saved answer reads "you can't work on Mondays or
Thursdays". `Piotr` scored, but the answer only says he "seems to be" her contact.

The instruction was followed, and that's the trouble. The model copied the value, and dropped what the value
*was*. The user's sentence has both: "My locker is number 212." So keeping the words isn't about style. It's
what keeps the label on the fact.

Be fair to the model: these bare notes came from this one prompt. Section 2's prompt kept "Locker number is 212", and
the `remember` tool's notes mostly kept their labels too, with "Johanna is known as Hana" as the exception. A note in
the model's words is only as good as that prompt on that day. A note in the user's words doesn't depend on a prompt at
all.

## 6. How much was the prompt?

Before you decide against "code checks", test it. It missed four facts, and one sentence in `CHECK` looks guilty: "A
question is not a fact." [code/wording.py](code/wording.py) tries three wordings:

```python
NO_RULE = CHECK.replace(" A question is not a fact.", "")
WORDINGS = {
    "as written": CHECK,
    "no question rule": NO_RULE,
    "in passing": NO_RULE.replace("state a fact about the person writing it", "say anything about the person writing it, even in passing"),
}
```

The third also changes "state a fact" to "say anything, even in passing". Each of the five runs keeps the messages
picked, in her words, and runs `recall` on them. It's about 720 model calls, so you don't have to run it. **Predict:** how much will removing that one sentence help?

```bash
python3 wording.py
```

```text
Wording            Facts picked  Unwanted  Recall
as written               8 to 8    0 to 0   37/60
no question rule         7 to 9    0 to 0   41/60
in passing             12 to 12    4 to 4   60/60
```

`as written` is the same setup as "code checks", and it scored 37 here against 39 in section 3. That's how much one setup
moves on its own. Removing the sentence, at 41, is barely more than that. The other change took it to all 12 facts and 60
of 60, with 4 unwanted notes. That's as good as anything in this chapter.

So we should be careful. Section 3 looked like a contest between code and the model, and a lot of that gap was **one
phrase in a prompt**. Here's what to take from it:

- A detector depends on its wording. Test yours, and expect a small change to matter.
- We wrote "in passing" after reading these failures, on this chat. It may do worse on a chat it wasn't written for. It's
  a direction, not a result.
- It's still a model call on every message: 36 here, whether or not she says anything worth keeping. The tool costs an
  extra call only when it saves.
- Either way, what's saved is her words. That part held in every setup that used it.

The finished `Memory` uses the tool, because the decision then sits in the agent you already have, with no second prompt
to look after. That's a design choice. These numbers don't prove it's the better one, and exercise 6 lets you test it.

## 7. Read the class

Here's what you've decided so far. The model chooses when to save. The code keeps the user's words. And
the notes have to outlive the program. All of that fits in
[code/whitebox/memory.py](code/whitebox/memory.py). Here's the first half:

```python
class Memory(Hook):
    """Notes in a JSON file, oldest first. The model says when to save. The code keeps the user's own words."""

    def __init__(self, path, today=date.today):
        self.path = Path(path)
        self.today = today
        self.latest = ""
        self.notes = json.loads(self.path.read_text()) if self.path.exists() else []

    def before_model(self, messages):
        """Remember what the user just said, so the tool can save their words and not the model's."""
        said = [message.content for message in messages if message.role == "user"]
        self.latest = said[-1] if said else ""
```

- `Memory` is a `Hook`, from chapter 16. `before_model` runs before every model call and sees all the
  messages, so it can note the latest thing the user said.
- `today=date.today` passes the function itself, with no brackets. `Memory` calls it when it needs a date.
  The tests pass in their own function, so a test always sees the same day.
- If the file exists, the notes come from it. That one line is what a new session reads.

Now the part that writes:

```python
    def add(self, text):
        """Save a note at the end, moving it there if we have it already, because the newest note wins."""
        if not text:
            return
        self.notes = [note for note in self.notes if note["text"] != text]
        self.notes.append({"text": text, "saved": self.today().isoformat()})
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.notes, indent=1))
        os.replace(temporary, self.path)
```

`append` is the whole of the ordering. A note goes on the end, so the list is oldest first, and that's
worth more than it looks. Section 10 measures it. The line above it takes out any note with the same words, so
a repeat moves to the end with today's date, because the newest note wins.

The last two lines are new Python:

- `with_suffix(".tmp")` gives the same path with a different ending: `hana.tmp` for `hana.json`.
- `os.replace(a, b)` renames `a` to `b`, replacing `b` if it's there. The operating system does that in one
  step. So if the program dies halfway through writing, the half-written file is `hana.tmp`, and `hana.json`
  is still the last good version. Writing straight to `hana.json` could leave you with half a file and no
  notes.

Then the tool, and the prompt:

```python
    def tool(self):
        """The tool that lets the model decide when to save."""

        @tool
        def remember(fact: Annotated[str, "What's worth keeping, in a few words"]) -> str:
            """Save something the user told you about themselves, for future conversations."""
            self.add(self.latest)
            return "Saved."

        return remember

    def system(self, text):
        """Add the notes to a system prompt, in the order they were saved, so the newest comes last."""
        if not self.notes:
            return text
        lines = "\n".join(f"- {note['text']}" for note in self.notes)
        return f"{text}\n\nThings this person told you before, oldest first:\n{lines}"
```

Read `remember` closely. **It never uses `fact`.** The model fills that argument in, the tool ignores it,
and `self.latest` is what's saved. So the model's only power is to make the call happen. Whatever it writes
in `fact`, a bare `212` or a flapjack full of nuts, can't reach the file. There's a test for exactly that
in `tests/test_memory.py`: the fake model calls `remember` with "user is 2 metres tall", and the note is
what the user said.

This is the same shape as `search_tool` in chapter 23: a tool defined inside a method, so it can use `self`
after `tool` has returned.

Using it takes three lines of wiring:

```python
memory = Memory("hana.json")
agent = Agent(load_model(), Toolbox([memory.tool()]), system=memory.system(REMEMBER_SYSTEM), max_steps=4,
              options=OPTIONS, hooks=[memory])
```

`memory` goes in twice, once as a tool and once as a hook, because it does two jobs. `agent.py` hasn't
changed at all.

## 8. Notes on disk

[code/session_one.py](code/session_one.py) is a short session with the wiring above. Six messages go in, each with
the history so far, and the script prints how many notes there are after each:

```python
history = None
for text in CHAT:
    result = agent.run(text, history)
    history = result.messages
    print(f"{len(memory.notes)} notes after: {text}")
```

**Predict:** which of the six will be saved?

```bash
python3 session_one.py
cat hana.json
```

```text
1 notes after: Hi, I'm Hana Kowalski, I've just joined the Old Mill branch.
1 notes after: How do I report a broken grinder?
2 notes after: My locker is number 212.
2 notes after: Can't do Thursdays, I've got a night class in bookkeeping.
2 notes after: The oat milk delivery came two hours late today.
2 notes after: Thanks, that's useful!
$ cat hana.json
[
 {
  "text": "Hi, I'm Hana Kowalski, I've just joined the Old Mill branch.",
  "saved": "2026-11-06"
 },
 {
  "text": "My locker is number 212.",
  "saved": "2026-11-06"
 }
]
```

That's the whole of Memory: a JSON file you can open, read and edit. It's in `code/`, and this chapter's
`.gitignore` has `code/*.json`, so your notes won't end up in git. Real notes about a person shouldn't.

The grinder question, the oat milk and the thanks weren't saved, which is the judgement we wanted. But look
again. **"Can't do Thursdays" wasn't saved either.** The model simply didn't call `remember` for it, in this run.
Nothing failed. There's no error and no warning. It's only a note that isn't there.

That's the price of letting the model decide. Hold on to it, and start a new program.

## 9. A new session reads it back

[code/session_two.py](code/session_two.py) has no history and shares nothing with session one. It's a separate
Python process. All it has is the file:

```python
memory = Memory("hana.json")
print(f"Read {len(memory.notes)} notes")
agent = Agent(load_model(), Toolbox([memory.tool()]), system=memory.system(REMEMBER_SYSTEM), max_steps=4,
              options=OPTIONS, hooks=[memory])
```

`memory.system` puts the notes into the system prompt, so they're in front of the model from its first call. Then
the script asks three questions, once each to show the answer, and five times each to count. **Predict:** which of
the three will it get?

```bash
python3 session_two.py
```

Answers are cut at 135 characters by us:

```text
Read 2 notes
What's my locker number? Your locker number is 212. Is there anything else you need help with?
Which day can't I work? I don't have information about your work availability. Could you please tell me which day you're unavailable?
Which branch am I at? You are at the Old Mill branch, Hana.
5/5  What's my locker number?
0/5  Which day can't I work?
5/5  Which branch am I at?
Notes now: 2
```

Compare that with section 1. Same model, same question, a new session, and now the locker comes back: 5 of 5,
against 0 of 5. The branch comes back too, from a sentence that was mainly a hello. That's what keeping her words
buys you: nobody chose to save "Old Mill", and it was in the sentence.

The Thursday question fails, 0 of 5, and it's honest about it. It can't know what was never saved. And `Notes now:
2` means asking questions added no junk, this time.

Six messages prove little, so [code/whole_chat.py](code/whole_chat.py) runs the finished class on all 36 messages, five
times. It deletes the file before each run, and uses `Path.unlink(missing_ok=True)` to do it: `unlink` deletes a file, and
`missing_ok=True` means it's fine if there's nothing to delete. Then it asks the 12 questions in new sessions:

```python
for text in chat():
    agent.run(text)
notes = [note["text"] for note in Memory(NOTES).notes]
answers = recall(model, memory.system(SYSTEM))
```

`Memory(NOTES)` reads the notes back from disk, so what's scored is what the file holds. It's about 300 model calls, so
you don't have to run it.

```bash
python3 whole_chat.py
python3 read_notes.py Memory
```

```text
run 1: 11 of 12, 13 notes, 2 unwanted
run 2: 12 of 12, 15 notes, 3 unwanted
run 3: 11 of 12, 14 notes, 3 unwanted
run 4: 11 of 12, 13 notes, 2 unwanted
run 5: 12 of 12, 14 notes, 2 unwanted

Unwanted notes in Memory, with how many runs saved each:
1  A customer left a blue scarf on table 4, what do I do with it?
5  Harbour was packed when I dropped in earlier.
5  Marek on the next till is off with flu.
1  The oat milk delivery came two hours late today.
```

57 of 60, with every note in Hana's words. Don't rank that against `user's words`: 57 and 59 are too close, and the two
differ only in small ways, such as the tool's wording. The knee is the fact that goes missing, in 3 runs of 5. In one run, asked about her health, the model replied with her allergy.

The unwanted notes are the same kind as before. "Harbour was packed" and Marek's flu were saved in all five runs. They're
harmless here, and they're in her words, so a later session can at least see what they are.

## 10. Out-of-date facts

Facts change. Hana moves branch. Notes are only ever added, so her file now says two things:

```text
- I'm Hana Kowalski, I work at the Old Mill branch.
...
- I've moved to the Harbour branch now.
```

[code/stale_notes.py](code/stale_notes.py) sets that up properly. There are 8 notes from February and March, and 4
updates from June: a new branch, a new day she can't work, a new locker and a new rota. Filling up the list are 48
harmless diary notes, such as "On shift 3 I worked with Lena and drank a chai." That makes 60.

Then it builds the system prompt in different ways, and asks 9 questions in each, five times over:

| Setup | The notes |
|---|---|
| `12 in order`, `60 in order` | What `Memory.system` gives you: oldest first, no dates |
| `60 newest first` | The same list backwards, so every old note comes after its update |
| `60 shuffled` | A different random order in each of the five runs |
| `60 shuffled + dates` | The same, with each date shown, and the rule "the newest date is true" |
| `12 replacing old` | Ask the model if each update replaces each old note, and delete the ones it says yes to |

The last one is the tidy idea: why keep a stale note at all? **Predict:** which setup gives the most old answers? And
what will replacing cost you?

The full run is about 300 model calls, so you don't have to do it.

```bash
python3 stale_notes.py
```

```text
Setup                Right Stale Both   Same Before Old last  Tokens
12 in order          20/20     0    2  20/20    5/5   0 of  0     208
60 in order          20/20     0    9  20/20    5/5   0 of  0     990
60 newest first      10/20    10    4  20/20    5/5  10 of 20     987
60 shuffled          18/20     2    4  20/20    5/5   2 of  6     987
60 shuffled + dates  19/20     1    1  20/20    5/5   1 of  6    1718
12 replacing old     20/20     0    5  20/20    0/5   0 of  0     175
Replacing took 35 calls and removed 2 of the 4 old notes:
  - I'm Hana Kowalski, I work at the Old Mill branch.
  - I'm on the 06:15 opener rota.
```

The columns: `Right` is answers naming the new value, out of 20. `Stale` gives only the old value. `Both` names both,
and those also count as `Right`. `Same` is the four facts that didn't change. `Before` asks "Which branch did I work
at before this one?". `Old last` counts stale answers, out of the times the old note came after the new one.

Read them in turn:

- **In order, nothing was stale, at 12 notes or at 60.** The `Both` answers here are fine when you read them: "Your
  opener rota is at 07:30. Previously, it was at 06:15". Three of the nine open badly, "You can't work on Tuesdays and
  Thursdays", and then correct themselves.
- **Backwards, half the answers went wrong.** The same 60 notes, in the other order. The branch and locker questions
  were stale in all 5 runs: "Your locker number is 212." `Right` is also generous here, because answers such as "Your
  opener rota is at 06:15. However, you've switched..." count as right. An earlier run of this script gave 8 of 20.
- **Shuffling hurt much less than we expected, and the `Old last` column says why.** In a random order, the old note
  came last in only 6 of 20 chances. Every stale answer in the table came from a case where the old note was last.
  The problem isn't disorder. It's an out-of-date note sitting after the fact that replaced it.
- **Dates didn't clearly help.** 18 against 19 is too close to rank, and 2 of 6 against 1 of 6 is too few to read. An
  earlier run got 20 of 20 with dates. What we can say is that the dates cost more: 1,718 tokens against 987.
- **Replacing cost the most, and did the least.** It took 35 model calls, and it deleted only 2 of the 4 old notes. The
  other two stayed, and the answers were still right, because the newest note came last. And it destroyed something:
  `Before` fell to 0 of 5, against 5 of 5 everywhere else. The old branch is gone, so the model says it's "not specified".

So the fix was already in the class. `self.notes.append` keeps the order, and `Memory.system` says "oldest first".
The order is a fact, and your code knows it for free. So keep it in code, instead of asking a model to work it out.

Notice what the model still does here: it reads both notes and picks the later one, which is a judgement. The code
just makes sure the later one really is later.

One caution. This is one set of changes, on one model, and each update says plainly that it's an update ("now", "new",
"switched"). A quieter change might be harder.

## 11. Why there's no search here

Part 4 spent five chapters on search, so why not search the notes? Look at the last column of that table. All 60 notes
came to 987 tokens, and the model answered from them. Every note fits in the prompt, so there's nothing to choose
between. Search would add a way to miss a note, and it would give you nothing back.

There's a second reason, and section 10 is it. A search returns the best matches by score, so an old note could land
after a new one, which is the case that went wrong. If you ever have too many notes to paste, you'll want a search, and
then you'll want your code to sort the hits by `saved` before the model sees them. We haven't tested that, so treat it
as a plan. Chapter 24's budget tells you when you've reached that point, and exercise 4 builds the simplest limit.

## 12. Two weak spots

`Memory` isn't finished, and it's better that you know where. [code/weak_spots.py](code/weak_spots.py) tries two things
we were suspicious of. First, Hana says something, changes it, then says the first thing again, in the same words:

```python
SAID_AGAIN = [
    (["My locker is number 212.", "My locker is number 87.", "My locker is number 212."], "What's my locker number?"),
    (["Can't do Thursdays.", "Thursdays are fine now.", "Can't do Thursdays."], "Can I work on Thursdays?"),
]
```

The second part tells the agent a fact, and then says "Please save that for next time." **Predict:** will the model
follow the newest note both times? And what's in the file after the second part?

```bash
python3 weak_spots.py
```

Answers are cut at 100 characters by the script:

```text
Notes kept: ['My locker is number 87.', 'My locker is number 212.']
   Your locker number is 212.
   Your locker number is 212. The previous statement about locker number 87 appears to be a correction 
   It seems there's a bit of a mix-up there. You mentioned your locker is number 87 and then 212. Could
   Based on the information you provided, your locker number is 212. The earlier locker number you ment
   Your locker number is 212. It appears there was a change from 87 to 212.
Notes kept: ['Thursdays are fine now.', "Can't do Thursdays."]
   Based on the information provided, it seems there was a change in availability for Thursdays. Initia
   Based on the information provided, it seems there was a change in availability for Thursdays. Initia
   Based on the information you provided, it seems there was a change in availability for Thursdays. In
   It seems there might be a bit of a mix-up. Previously, you mentioned "Can't do Thursdays" and later 
   It seems there's a bit of a mix-up with Thursdays. Earlier, you mentioned "Can't do Thursdays," but 
run 1: ["Can't do Thursdays, I've got a night class in bookkeeping."]
run 2: ["Can't do Thursdays, I've got a night class in bookkeeping."]
run 3: ["Can't do Thursdays, I've got a night class in bookkeeping."]
run 4: ["Can't do Thursdays, I've got a night class in bookkeeping."]
run 5: ["Can't do Thursdays, I've got a night class in bookkeeping."]
```

**The order is right, and that's not always enough.** Both lists end on what she said last, because `add` moved the
repeat. For the locker, 4 of 5 runs gave 212, and one asked her to clear it up. With Thursdays, every answer calls it a
change or a mix-up. When we printed more of each answer, in an earlier run, none of the five gave a plain "no". Some
said she could work, and some said to check. Our guess is the word "now" in the older note, which sounds newer than
it is, but we didn't test that. Order helps the model. It doesn't decide for it.

**A note can be the request itself.** The tool saves the latest message, so if the fact was in an earlier one, the note
can be `Please save that for next time.` This run shows 0 of 5, and two earlier runs of this script each showed 1 of 5,
so it's about 2 runs in 15. No fact was lost in any of them, because the model had also saved the Thursdays message.
Compare that with section 8, where the same sentence wasn't saved. It's the same model making the same call differently
from one run to the next.

## What this does and doesn't show

- **One person, one chat, one 7B model.** The prompts came from work on a different chat, so this was a fresh test for
  them, except `in passing`, which we wrote after seeing these failures. A bigger model may rewrite more carefully, or
  decide differently. Measure yours.
- **Scores within a few points can't be separated.** 57 and 59 can't, and neither can 18 and 19.
- **A right answer means the right word appeared.** We read the answers, and `Both` in section 10 shows why you must.
- **Each message in sections 3 and 9 was its own run.** A real session has history, as `session_one.py` does, and that may
  change what the model saves.
- **Nothing here deletes a note.** The file grows forever, and it holds what a person said, in plain text. Exercise 3 adds
  `forget`, and exercise 5 stops some things being saved at all.

## Reading errors

The first is the error you met in chapter 20. We triggered the others for real.

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You ran `session_two.py` first | No error. It prints `Read 0 notes`, and then the model doesn't know | Run `session_one.py` first |
| The notes file is cut short, or you broke it by hand | `json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes` | Fix the file, or delete it and start again |
| The file is a plain list of strings, not `text` and `saved` | `TypeError: string indices must be integers, not 'str'` | Each note must be `{"text": ..., "saved": ...}` |
| The notes path is in a folder that doesn't exist | `FileNotFoundError: [Errno 2] No such file or directory: 'nofolder/notes.tmp'` | Make the folder first. Look at the name: it's the temporary file that failed |

## Exercises

From `chapters/25-memory`, open [exercises.py](exercises.py) and complete the five TODOs:

1. `unwanted`: find the notes that hold none of the facts you hoped to save.
2. `recall_score`: ask each question in a new session, and count the right answers.
3. `forget`: delete notes on request, and write the file safely. Hana can ask you to.
4. `Budgeted`: keep the notes in the prompt inside a token budget, using chapter 24's `newest`.
5. `Private`: a hook that refuses to save messages holding words you've blocked.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find the `whitebox` package
inside `code/`.

Then check your work from `chapters/25-memory`. These checks use a fake model, so Ollama doesn't need to be
running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

**Exercise 6, optional: test someone else.** Everything here was measured on Hana. Copy `hana.py`, write a
different person with their own 12 facts, and run `who_decides.py` on them. Do the same facts go missing, the
ones tucked behind a question? There's no worked answer, because it's your person.

## Common mistakes

- **Saving the model's summary of a fact.** `212` is exact, and it's useless without the word "locker".
- **Trusting a score without reading the notes.** The flapjack note cost no points.
- **Assuming the model will save what matters.** "Can't do Thursdays" went unsaved in section 8, with no error.
- **Comparing setups and forgetting the prompt.** One phrase moved "code checks" from 8 facts to 12.
- **Deleting old notes to keep things tidy.** It took 35 calls, missed 2 of 4 changes, and lost "which branch before?".
- **Sorting notes any way but oldest first.** Backwards, the same 60 notes gave stale answers in 10 of 20.
- **Writing the notes file directly.** Use a temporary file and `os.replace`, so a crash can't leave half a file.
- **Adding search because you can.** 60 notes came to under 1,000 tokens.

## Recap

- A new session has nothing but what you give it: 5 of 5 in the same session, and 0 of 5 in a new one.
- `Memory` keeps notes in a JSON file, adds them to the system prompt, and writes through a temporary file and `os.replace`.
- The model says when to save. The tool ignores what it wrote, and saves the user's own words.
- On Hana's chat, recall in a new session was 39 of 60 for code checks as first written, 50 for the model's words, 59 for
  the user's words, and 57 for the finished `Memory`.
- Rewriting went wrong in quiet ways: a bare `212` became "Your locker number is 5093" in 5 runs of 5, a question became
  "The flapjack contains nuts", and "badge" fell out of a note.
- Stale answers came only when an old note sat after its update. In order, 0 stale of 20, at 12 notes and at 60.
- So the order stays in code. Replacing old notes cost more and lost history.
- A repeat moves to the end, because the newest note wins.
- Two weak spots remain: words such as "now" in an older note can outweigh the order, and a note can be "Please save
  that".

The model made the judgement call. The facts and the order stayed in code.

## Where this comes from

Keeping a growing record of what an agent has seen, and reading it back later, comes from the 2023 paper
[Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442). Having a model
manage its own memory with tool calls comes from
[MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560).

**Next:** chapter 26 goes back to the two-fact questions that chapter 23 left unsolved, with a plan.
