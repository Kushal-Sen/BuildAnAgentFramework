# Chapter 26: Planning patterns

**Time:** about 2 hours. The hop test is optional. **You'll build:** a plan that's written first and carried out
step by step, with each search using what the earlier steps found. Then you'll measure what it buys, what it costs, and
what the test can't tell you.

## Where we are

Chapter 23 ended with an unsolved problem. "How much notice must a shift lead give?" needs two facts: the shift lead's
band, and the rule for that band. The agent almost never searched twice. `Split` forced the extra searches in code, and
both files came back about half the time.

There's a limit built into `Split`, though. It writes every search before it has seen a single result. So no search
can use anything the handbook said. This chapter tries the obvious next step: search, read, then write the next search.

The thread of Part 5 carries on: **let the model make the judgement call, and keep the facts, the order and the truth in
code.** Here the model writes the steps, and your code makes sure each one happens. The result isn't the one you'd
hope for, so read this chapter for the method as much as for the pattern.

## Before you start

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in chapter 05. You also need
`nomic-embed-text` from chapter 19. You'll work in `chapters/26-planning-patterns/code`.

One file is new in the framework: `whitebox/planning.py`. `agent.py` doesn't change, and `Plan` doesn't use the agent loop
at all. These things are provided, and you don't need to change them:

- `questions.py` and `library.py` are from Part 4, with the six hop questions, the strict check from chapter 23, and
  `build_agent`, `files_seen` and `Remember`.
- `hop_setups.py` holds the setups we compare. `Split` is chapter 23's, moved here. Section 5 explains the rest.
- `results/` holds our saved tests. `plan_scores.py`, `plan_read.py`, `plan_plans.py` and `plan_control_scores.py` read
  them, and they use your own files if you've made them. So **you can follow the whole chapter without the long tests.**
- `plan_test.py` and `plan_control.py` are measuring scripts. Each section shows the part that matters.

To check the framework itself, run this from `code`:

```bash
python3 -m pytest tests
```

You should see `77 passed`. These tests use a fake model, so they don't need Ollama.

## 1. Two facts, six tries

Open [code/two_facts.py](code/two_facts.py). It asks the plain agent and `Split` one question, three times each, and
prints what each run searched, which files came back, and the start of the answer:

```python
for label, setup in (("Plain agent", build_agent(model, index)), ("Split", Split(model, index))):
    print(label)
    for _ in range(3):
        result = setup.run(QUESTION)
        queries, seen = what_it_did(result)
        print("  Searched:", " | ".join(queries))
        print("  Files:   ", " ".join(files_seen(seen)))
        print("  Answer:  ", result.answer[:100].replace("\n", " "))
```

The answer needs `pay-bands.md`, which says a shift lead is Band C, and `resignation.md`, which says Band C gives 4
weeks. **Predict:** how many of the six runs see both files?

```bash
python3 two_facts.py
```

This is real output from `qwen2.5:7b`:

```text
Plain agent
  Searched: shift lead resignation notice period
  Files:    breaks-and-staff-drinks.md resignation.md shifts.md
  Answer:   As a shift lead, you must give your resignation notice according to your Band level. Band A and Band
  Searched: shift lead resignation notice
  Files:    resignation.md rota-swaps.md shifts.md
  Answer:   As a shift lead, you must give your resignation notice based on your Band level. Band A and Band B s
  Searched: shift lead resignation notice period
  Files:    breaks-and-staff-drinks.md resignation.md shifts.md
  Answer:   As a shift lead, you must give your resignation notice according to your band. Band A and Band B sta
Split
  Searched: What is the notice period required for shift leads in the staff handbook? | What are the resignation policies for management roles in the staff handbook? | What are the specific requirements for notice periods when resigning from a shift lead position?
  Files:    breaks-and-staff-drinks.md forms.md resignation.md rota-swaps.md shifts.md welcome.md
  Answer:   You must give 2 weeks' notice as a shift lead, which would be Band A or Band B based on the informat
  Searched: What is the notice period required for shift leads to resign according to the staff handbook? | What group does the shift lead position fall under in the staff handbook? | What are the resignation procedures outlined for shift leads in the staff handbook?
  Files:    breaks-and-staff-drinks.md pay-bands.md resignation.md rota-swaps.md shifts.md
  Answer:   You must give 4 weeks' notice when you resign, as you are in Band C. [resignation.md]
  Searched: When must a shift lead provide notice of resignation? | What is the notice period required for a shift lead? | Are there specific guidelines for notice periods in the staff handbook for shift leads?
  Files:    breaks-and-staff-drinks.md resignation.md rota-swaps.md shifts.md
  Answer:   You must give 8 weeks' notice when you resign, as you are Band E staff. [resignation.md]
```

One of six. The agent searched once each time, found the rule, and listed the bands. `Split` searched three times, and
gave three different answers: 2 weeks, 4 weeks and 8 weeks. Only the run that saw `pay-bands.md` was right. The other two
picked a band.

## 2. What Split can't do

Look at `Split`'s searches again. They're all questions about shift leads and notice. None could say "Band C", because
when they were written, nothing had been read.

Try it the way a person would. [code/by_hand.py](code/by_hand.py) has no chat model, only two searches, and you read the
first result before you write the second:

```python
show("What band is a shift lead?")
# Read that. Now you know a word the question never said.
show("How much notice does Band C give?")
```

```bash
python3 by_hand.py
```

The script cuts each hit at 150 characters:

```text
Search: What band is a shift lead?
  [pay-bands.md] # Job roles and bands Every role belongs to a band. - Trainee barista: Band A - Barista: Band B - Senior barista: Band C - Shift lead: Band C - Assist
  [rota-swaps.md] # Swapping a shift You may swap a shift with a colleague of the same band or higher, as long as the swap doesn't take either person above 48 hours in 
  [rota-swaps.md] Swapping a shift Post the swap in StaffHub at least 24 hours before the shift. It is confirmed only when the other person accepts and your manager app
Search: How much notice does Band C give?
  [resignation.md] # Leaving Quillon To resign, give your branch manager written notice. Band A and Band B staff must give 2 weeks. Band C and Band D staff must give 4 w
  [wages.md] Wages Band E is salaried. Sunday hours are paid at time and a quarter. Hours worked on a public holiday are paid at time and a half. If your pay looks
  [bereavement-leave.md] # Bereavement leave If a close relative dies, you may take up to 5 days of paid leave. A close relative means a partner, child, parent or sibling. For
```

`pay-bands.md` comes first for the first search, and `resignation.md` first for the second. The second search says
"Band C", and that came from reading the first result. That's the new idea: **a later search can use what an earlier
step found.**

Now get the model to do it. There are two things you did there that it has to do: decide what to look up, and carry
what you learned into the next search.

## 3. Write a plan

Here's the prompt in [code/whitebox/planning.py](code/whitebox/planning.py):

```python
PLAN = (
    "Question: {question}\n\nWrite a short plan for answering this from a staff handbook. List the facts to look up, "
    "in order, one per line, at most 3. A later step can use what an earlier step finds. Write nothing else."
)
```

And the code that asks for it:

```python
def clean(line):
    """Strip the bullets, numbering and quotes a model puts around a line, and keep the words themselves."""
    return re.sub(r'^[\s*"-]*(\d+[.)](?!\d)\s*)?', "", line).strip(' *".')
```

```python
def make_plan(self, question):
    lines = self.ask(PLAN.format(question=question)).splitlines()
    return [clean(line) for line in lines if clean(line)][:3]
```

`re` is Python's module for **regular expressions**, a short way to describe a pattern in text. `re.sub(pattern, "", line)`
finds the pattern and replaces it with nothing. The `r` before the quote keeps each backslash as it's written. This
pattern has four parts:

| Part | Means |
|---|---|
| `^` | The match must start at the beginning of the line |
| `[\s*"-]*` | Any number of spaces, stars, quotes or dashes. `\s` is any space, and the final `*` means "as many as there are" |
| `\d+[.)](?!\d)\s*` | Numbering: one or more digits, then `.` or `)`, then any spaces. `(?!\d)` means "not followed by a digit", so `2.5 hours` stays whole |
| `( ... )?` | The `?` makes the numbering optional, so a line without it still matches |

Then `strip` tidies the ends. With an argument, it removes any of those characters from both ends of a string, in any
order. So `1. "Find the band"` becomes `Find the band`.

The rest of the line stays. Digits are only removed as numbering at the very start, so `2. Find form IR-7` becomes `Find form
IR-7`, and `2025 rota changes` keeps its year. A label stays too: `Step 1: Find the band` comes back unchanged, because it
doesn't start with a bullet or a number. Exercise 3 deals with that.

[code/first_plans.py](code/first_plans.py) asks for two plans, and searches for nothing:

```python
for question in QUESTIONS:
    print(question)
    for step in planner.make_plan(question):
        print("  -", step)
```

**Predict:** will the first plan say to find the shift lead's band?

```bash
python3 first_plans.py
```

```text
I'm a shift lead. How much notice must I give when I resign?
  - Review the resignation policy outlined in the staff handbook
  - Check if the handbook specifies a notice period for shift leads
  - Determine if there are any exceptions or special conditions for resignation
I'm opening the Harbour branch on a Monday. What time do I need to arrive?
  - The opening hours for the Harbour branch on Monday
  - The address and location of the Harbour branch
  - The standard opening time for new branches
```

No. It's tidy, and it looks like a plan. It's also what you'd write for any question about any handbook. The second one
never mentions the time you have to arrive. Keep that in mind. We'll count these in section 8.

## 4. Carry it out

Here's `run`, the whole pattern:

```python
def run(self, question):
    steps = self.make_plan(question)
    hits, known, queries = [], [], []
    for step in steps:
        query = clean(self.ask(QUERY.format(step=step, known="\n".join(known)))) if known else step
        found = self.index.search(query, self.k)
        have = {hit.text for hit in hits}
        hits += [hit for hit in found if hit.text not in have]
        queries.append(query)
        known.append(self.ask(FIND.format(excerpts=excerpts(found), step=step)))
    notes = "\n".join(known)
    asked = f"Excerpts:\n\n{excerpts(hits)}\n\nNotes from the search:\n{notes}\n\nQuestion: {question}"
    messages = [Message("system", ONE_ANSWER), Message("user", asked)]
    reply = self.model.chat(messages, **self.options)
    result = Result(reply.content, messages + [reply], 2 * len(steps) + 1)
    result.plan, result.queries, result.seen = steps, queries, excerpts(hits)
    return result
```

Take it a line at a time:

- **The first step is searched as it's written.** Nothing is known yet, so there's nothing to use.
- **Each later step gets a new search.** `QUERY` shows the model the step and everything in `known`, and asks for one
  short search query. This is the line `Split` doesn't have.
- **`FIND` writes the note.** It shows the model what came back, and asks what answers this step, in one sentence, or
  "not found". The note goes into `known`.
- **The last call answers**, from all the hits and all the notes, with chapter 23's "don't list every option" rule.

Your code owns the loop. The model can't stop early and can't skip a step, which is the lesson from chapter 23: it wouldn't
choose a second search, so don't ask it to.

[code/plan_once.py](code/plan_once.py) runs it once and prints every step. `zip` walks through several lists together,
one item from each at a time. `Counted`, explained in the next section, counts the calls:

```python
for step, query, note in zip(result.plan, result.queries, notes.split("\n")):
    print("Step: ", step)
    print("Query:", query)
    print("Found:", note)
```

```bash
python3 plan_once.py
```

We ran it four times. It was right once. Here are the first two runs, in the order they came:

```text
Step:  Review the staff handbook for the resignation policy
Query: Review the staff handbook for the resignation policy
Found: Band E staff must give 8 weeks' notice when resigning.
Step:  Identify the specific section related to shift leads
Query: Band E staff resignation notice period
Found: not found
Step:  Check if there are any exceptions or additional requirements for shift leads
Query: shift leads resignation notice period Band E
Found: not found
Files: annual-leave.md log-old-mill-2025-04.md log-station-2025-03.md pay-bands.md resignation.md shifts.md wages.md
Answer: You must give 4 weeks' notice when resigning, as a shift lead is categorized under Band C, and Band C staff must give 4 weeks' notice according to the resignation guidelines. [resignation.md]
Model calls: 7
```

```text
Step:  Review the resignation policy outlined in the staff handbook
Query: Review the resignation policy outlined in the staff handbook
Found: Band E staff must give 8 weeks' notice of resignation.
Step:  Check if the handbook specifies a minimum notice period for shift leads
Query: Band E staff notice period shift leads
Found: not found
Step:  Determine if there are any additional clauses for resignations by shift leads
Query: Band E staff resignation notice period
Found: not found
Files: annual-leave.md log-old-mill-2025-04.md resignation.md shifts.md wages.md
Answer: You must give 8 weeks' notice when you resign, as you are Band E staff. [resignation.md]
Model calls: 7
```

Read these slowly, because almost everything in this chapter is here.

- **The chain worked.** The second query in each run uses something the first step found. `Split` can't do that.
- **What it carried was wrong.** The excerpt listed every band, and the one-sentence note kept only the last one: "Band
  E". The next searches then went looking for Band E.
- **The first run was right by luck.** No step asked for the shift lead's band. One search, "shift leads resignation
  notice period Band E", happened to bring back `pay-bands.md`, as its third hit. The final answer read the file and
  ignored the wrong note.
- **The second run had the same wrong note, missed that file, and said 8 weeks**, twice what's right.

So a run can be right without the plan doing what it looks like it did. One run proves little either way. Time to measure.

## 5. The test

Here's what we compare, in [code/hop_setups.py](code/hop_setups.py):

| Setup | Who decides to search again | Each later search sees earlier results |
|---|---|---|
| Plain agent | The model | Yes |
| `Split` | Code: one search per fact | No |
| Step by step | The model | Yes |
| `Plan` | Code: one search per step | Yes |

Step by step is new. It has `Plan`'s searching and notes, with no plan: it searches, writes a note, and then asks the
model for the next search or `DONE`. It's here so we can ask whether the plan matters, or just the notes:

```python
for _ in range(self.limit):
    found = self.index.search(query, self.k)
    hits = add_new(hits, found)
    queries.append(query)
    known.append(self.ask(FIND.format(excerpts=excerpts(found), step=query)))
    decision = self.ask(NEXT.format(question=question, known="\n".join(known)))
    if decision.upper().startswith("DONE"):
        break
    query = clean(decision.splitlines()[0])
```

`Counted` wraps a model and adds one to `calls` each time it's used, so the cost is measured, not worked out.

We need a better score than "right", and section 1 showed why: those `Split` runs picked a band, and a pick can land on the
right one. So we'll use two:

- **Strict** is chapter 23's check. The answer says the right value, and none of the wrong ones.
- **Earned** means strict, and the searches saw both files. The answer could have come from the facts.

[code/plan_test.py](code/plan_test.py) runs all four on the six hop questions, five times each:

```python
for name, _, question, answers, files in HOPS:
    for _ in range(RUNS):
        before = model.calls
        result = setup.run(question)
        queries, seen = what_it_did(result)
```

It saves every answer, search, plan and note. That's about 420 model calls, so you don't have to run it. We ran it twice,
as chapter 23 did, because one batch can mislead. If you want to:

```bash
python3 plan_test.py
python3 plan_test.py again
```

**Predict:** `Plan` makes 7 model calls and `Split` makes 2. How much better is `Plan`?

```bash
python3 plan_scores.py
```

```text
Setup          Strict  Earned  Calls  Searches  Calls per earned
Plain agent        21       0    2.0       1.1                 -
Split              20      16    2.0       2.8               7.5
Step by step       10       0    3.0       1.0                 -
Plan               20      14    7.0       3.0              30.0
60 runs each. Calls and Searches are per run.
```

And the two batches side by side, from `python3 plan_scores.py batches`:

```text
Setup               Strict      Earned   (first batch, second batch, 30 runs each)
Plain agent         11, 10        0,  0
Split               10, 10        8,  8
Step by step         5,  5        0,  0
Plan                10, 10        8,  6
```

Read it carefully:

- **`Plan` didn't beat `Split`.** Strict is 20 and 20. Earned is 14 and 16. That's too close to rank, either way. The
  honest result is a tie, and a tie at three and a half times the calls isn't a win.
- **The setups where code forces the searches earned something.** 16 and 14, against 0 and 0.
- **The setups that left it to the model searched about once, and earned nothing.** Step by step wrote `DONE` after the
  first search in all 60 runs. The plain agent searched again in 3. That's chapter 23 again.
- **So the notes alone did nothing.** Step by step had the notes, and scored the lowest.

## 6. What it cost

Each `Plan` run with three steps makes 7 calls: 1 for the plan, 3 notes, 2 queries, 1 answer. `Counted` confirms it. That's
`2 * len(steps) + 1`, the number you saw in `Result`.

`Calls per earned` is the total number of calls divided by the earned passes. `Split` paid 7.5 calls for each one. `Plan`
paid 30, four times as much. Every call is more waiting, and with a paid model, more money. So the question to ask of any
pattern isn't "does it work?". It's "what does each right answer cost?".

## 7. Question by question

Totals hide things. `python3 plan_scores.py questions` splits them, ten runs per cell:

```text
Strict / earned, out of 10 runs
Question             Plain agent         Split  Step by step          Plan
harbour-arrive             0 / 0         2 / 2         0 / 0         0 / 0
senior-beans               2 / 0         0 / 0         0 / 0         1 / 0
riverside-repair           8 / 0         4 / 4         0 / 0         4 / 2
shift-lead-pay             0 / 0         2 / 2         0 / 0         4 / 4
lead-notice                1 / 0         4 / 2         2 / 0         6 / 4
old-mill-repair           10 / 0         8 / 6         8 / 0         5 / 4
Needs both, of 40          3 / 0         8 / 6         2 / 0        11 / 8
```

Now remember chapter 23. **The two repair questions aren't really hops,** because each branch file holds the contractor's
number. One file is enough, so "earned" is too harsh there.

- **On those two, the plain agent is the best setup here:** 18 of 20, with one search and 2 calls. Its zero for earned
  says nothing bad about those answers. We read them, and they're right, from the branch file.
- **`Plan` scored 9 of 20,** below the agent and `Split`'s 12. It searches for the steps it wrote, and the steps often
  leave out the branch.
- **The last row is the four questions that do need both files.** Earned is 0 for the agent, 6 for `Split`, 8 for
  `Plan`. That's out of 40, so 8 against 6 can't be ranked. It's a hint at most. The agent's 3 strict passes there have
  no second file behind them.

Read what the unearned passes say. `plan_read.py` prints the saved answers for one question, and section 9 uses it
too. Here's the first unearned pass from three questions, marked `pass`:

```text
$ python3 plan_read.py senior-beans "Plain agent"
pass: As a senior barista, you get 25% off retail beans when you are off shift and using your staff card at any branch. [staff-discount.md]
$ python3 plan_read.py lead-notice Split
pass: You must give 4 weeks' notice when you resign as a Band C or Band D staff member. [resignation.md]
$ python3 plan_read.py riverside-repair
pass: I don't know. [branch-riverside.md] doesn't provide the contact number for equipment service, only that the contractor is Northline Service, 0300 555 0177.
```

The first picked the right row without knowing the band. The second never says which band a shift lead is. The third
says "I don't know", gives the number anyway, and passes the strict check. We read all 71 strict passes, and the earned
ones hold up: each states the value, and had both files behind it. That reading is the only reason to trust the column.

## 8. Read the plans

Maybe `Plan` found both files because it planned well. Let's check. `python3 plan_plans.py` counts the 60 saved plans:

```python
band = [run for run in runs if run["name"] in BAND_QUESTIONS]
print(f"  name the band: {sum(names_word(run, 'band') for run in band)}")
```

```text
Plans in all: 60
Mention the handbook, a section or a policy: 35
Three questions that turn on a band: 30 plans
  name the band: 0
  earned anyway: 8
harbour-arrive: 10 plans
  name the arrival time: 7
  earned: 0
```

Three questions turn on a band, and not one of their 30 plans says "band". They still earned 8 passes. And 7 of the 10
`harbour-arrive` plans name the arrival time, which is the right idea, and that question earned none. This is a rough word
count, and "handbook" comes partly from our own prompt. But on these counts, the plans that looked better didn't do better.

Judge some for yourself. Here are the first four `shift-lead-pay` plans, from `python3 plan_plans.py shift-lead-pay`, which cuts each step at 90 characters:

```text
earned
    Review the introduction section of the staff handbook for general information on pay struc
    Check the section detailing roles and responsibilities to find the definition of a shift l
    Identify and note the hourly rate associated with the shift lead role
earned
    Review the compensation section of the staff handbook
    Check the shift lead responsibilities to confirm eligibility
    Identify the hourly rate for shift leads as stated in the handbook
earned
    Review the staff handbook's compensation section
    Check the shift lead role description
    Identify the specific hourly rate for shift leads
FAIL
    Review the staff handbook's compensation section
    Check if the handbook specifies a general pay rate for shift leads
    Identify if there are any specific hourly rates mentioned for shift leads
```

Three earned and one failed. None says why it's looking, and none names the band. One thing does stand out: the three that
earned each have a step about the shift lead's role, and the failure doesn't. Across all ten plans for this question, 7
mention roles or responsibilities, and 4 of those earned. The other 3 earned none. That's small, but it's fair to say a
step's wording steers the search, whether or not the model meant it to.

So where did `Plan`'s earned passes come from? **This test can't say.** `Plan` changes several things at once:

- It searches about three times, against about once for the plain agent and step by step.
- Those searches use different words from the question, whether or not the plan is any good.
- Later searches see earlier notes.
- The final answer gets the notes as well as the excerpts.

`Split` also searches about three times, in different words, with no notes and no plan, and it earned just as much. So the
likeliest reading is that more searching did the work, not smarter planning. It's only the likeliest reading. We never
ran a setup that makes three generic searches with no plan at all. Exercise 6 is that test.

## 9. What Plan still fails

Three questions, three different failures. Each comes from `python3 plan_read.py`, which prints the saved answers and
searches. It cuts answers at 170 characters.

**`harbour-arrive`: 0 of 10.** `python3 plan_read.py harbour-arrive`, first three runs:

```text
FAIL: You need to arrive by 06:30 on a Monday. [branch-harbour.md]
    search: The operating hours for the Harbour branch
    search: What is the recommended arrival time for the Harbour branch on opening day?
    search: Search for "Harbour branch manager contact information
FAIL: You need to arrive by 06:30 on a Monday. [branch-harbour.md]
    search: The operating hours for the Harbour branch
    search: What is the recommended arrival time for staff opening the Harbour branch on weekdays and weekends?
    search: Harbour branch opening hours Monday to Friday and Saturday and Sunday
FAIL: You need to arrive by 06:30 on a Monday, as the branch is open from 06:30 to 16:00 on weekdays. [branch-harbour.md]
    search: The operating hours for the Harbour branch
    search: Harbour branch operating hours Monday to Friday and weekends
    search: What is the recommended arrival time for staff at the Harbour branch, considering it is busiest in t
```

The opening time is right, and it stops there. The rule is in `shifts.md`: arrive 30 minutes before opening. Not one of the
10 runs saw that file. The step was often right, "recommended arrival time for staff". Then the query added "Harbour
branch", from what was known, and that pulled the search towards Harbour's logs. Carrying earlier facts forward made this
search worse. `Split`, which can't do that, saw `shifts.md` in 4 of 10 runs, and passed 2.

**`senior-beans`: 1 of 10, none earned.** `python3 plan_read.py senior-beans`, first four runs:

```text
FAIL: I don't know. [staff-discount.md] mentions discounts for different bands but does not specify a discount for senior baristas.
    search: Step 1: Review the employee benefits section of the staff handbook
    search: Search for "employee benefits senior barista discount
    search: Search for: "employee benefits section requirements for staff discounts
FAIL: I don't know. [staff-discount.md] mentions discounts for different bands but does not specify a discount for senior baristas.
    search: Step 1: Check the employee benefits section of the staff handbook
    search: Search for "specific discount rate senior baristas retail beans
    search: Search for additional terms or conditions associated with the discount
FAIL: You get 30% off retail beans as a senior barista, which corresponds to Band C. [staff-discount.md]
    search: Step 1: Review the current employee discount policy
    search: senior baristas specific discount staff card branch drinks food retail beans
    search: Search for: "staff discounts percentages based on staff band for drinks, food, and retail beans
pass: Band C and Band D get a 25% discount on retail beans. [staff-discount.md]
    search: Step 1: Check the employee benefits section of the staff handbook
    search: Search for "specific discount details for baristas
    search: SELECT * FROM discount_requirements WHERE discount_type = 'drinks' AND guest_accompanied = 'yes' AND
```

Only 2 of 10 runs saw `pay-bands.md`, and no step asked for it. Look at the searches too. 64 of `Plan`'s 180 searches
start with "Search for" or similar, or are SQL for a database that doesn't exist. `clean` doesn't catch that, because the
words aren't punctuation. The one pass here gives a rule for two bands, and never says which band a senior barista is.

**`riverside-repair`: 4 of 10, 2 earned.** The plan's first step was usually "The contact number for maintenance
services", with no branch in it, and 5 of 10 runs never saw `branch-riverside.md`. The plain agent, which kept
the word "Riverside" in its one search, scored 8 of 10.

The pattern across all three: **a plan can drop what mattered in the question.** The search only knows the step, and the
step is the model's rewording.

## 10. The control

Does `Plan` break anything? [code/plan_control.py](code/plan_control.py) runs the same four setups on questions that need
no plan: 8 direct questions, and the 4 handbook questions with no answer, three runs each. An unanswerable one passes
only if it says "I don't know":

```python
good = says(answer, answers) if answers else "don't know" in answer.lower().replace("’", "'")
```

**Predict:** does a longer process make it invent an answer?

```bash
python3 plan_control.py
python3 plan_control_scores.py
```

Our run is saved, so the second line alone prints it:

```text
Setup           Direct  Unanswerable   Total  Calls
Plain agent      24/24         12/12   36/36    2.0
Split            24/24         12/12   36/36    2.0
Step by step     24/24         12/12   36/36    3.0
Plan             24/24         12/12   36/36    7.0
```

All four scored 36 of 36. We read the answers: the direct ones state the value, and the unanswerable ones decline, some
adding which files didn't help. So on these questions `Plan` did no harm. It also did no good. It paid 7 calls for what
2 calls got. Don't plan a question that doesn't need a plan.

## 11. What the numbers can and can't support

| Claim | Our evidence |
|---|---|
| Forcing the searches in code gets both files, and leaving it to the model didn't | Earned 16 and 14, against 0 and 0, of 60 |
| `Plan` costs 3.5 times `Split`'s calls | 7 against 2, measured |
| `Plan` did no harm on easy questions | 36 of 36, level with every setup |
| `Plan` beats `Split` | **Not shown.** 20 and 20 strict, 14 and 16 earned |
| `Plan` does better where both files are needed | **Not shown.** 8 against 6 of 40 is too close |
| Good plans caused `Plan`'s passes | **Not shown.** 0 of 30 named the band, and they earned 8. The test can't separate planning from more searching |
| Using earlier findings helps | **Mixed.** It did what it says, and it also carried "Band E" and bent the Harbour search |

The limits are real. This is six questions, one handbook and 60 runs per setup, two of the questions aren't true hops,
and the strict check was written after reading answers. Our prompts could be better: a one-sentence note is what lost the list
of bands. And we tested one 7B model. A bigger model may well write a plan that says "find the band". So don't read this
as "planning doesn't work". Read it as what happened here, and run `plan_test.py` on your own model.

| Your situation | What to try |
|---|---|
| One file holds the answer | The plain agent. It was the best setup on the repair questions, at 2 calls |
| The answer needs two facts, and calls matter | `Split`, in your code. It earned as much here for 2 calls |
| A later search can't be written until an earlier one is read | `Plan`, with the notes read and tested. This is what it's for, and our test didn't show it paying off |
| You're tempted to let the model choose when to stop | Measure first. Here it stopped after one search almost every time |
| Your documents fit in the window | Paste them, as chapter 23 found |

## Reading errors

We triggered each of these for real.

| What happened | What you see | The fix |
|---|---|---|
| Ollama isn't running | `whitebox.models.ModelError: Couldn't reach Ollama` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| You ran `plan_read.py` with no question | `IndexError: list index out of range` | Add one: `python3 plan_read.py lead-notice` |
| You misspelled a question or setup | No error, and nothing printed | Use a name from `questions.py`, or a setup as written in `plan_scores.py`'s table |
| You wrote `Plan(model, index, OPTIONS)` | `TypeError: cannot use 'tuple' as a dict key (unhashable type: 'dict')` | The third argument is `k`. Write `options=OPTIONS` |
| The note carried a wrong fact | No error at all. The next query says "Band E" | Print the notes with `plan_once.py` and read them |

## Exercises

From `chapters/26-planning-patterns`, open [exercises.py](exercises.py) and complete the five TODOs:

1. `earned`: right, and every needed file is in what the search saw.
2. `calls_per_earned`: what each earned pass cost, or `None` if nothing was earned.
3. `drop_label`: remove the `Step 1:` that `clean` leaves in.
4. `TidyPlan`: a `Plan` whose steps have no labels.
5. `plans_naming`: count the plans that name a word, as section 8 did.

The `sys.path` line at the top of `exercises.py` is provided. It lets the file find `whitebox` inside `code/`. Exercise 3
uses `partition`, from chapter 24: `"a: b".partition(":")` gives back `("a", ":", " b")`, and the middle part is empty if
there's no colon. Exercise 4 uses `super()`, also from chapter 24, to reach `Plan`'s own `make_plan`.

Then check your work from `chapters/26-planning-patterns`. These checks use a fake model and a fake embedder, so Ollama
doesn't need to be running:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in [solutions/exercises.py](solutions/exercises.py).

**Exercise 6, optional: separate the two.** Write a `FixedPlan(Plan)` whose `make_plan` ignores the model and returns the
same three generic steps for every question, then add it to `build_setups` in `hop_setups.py` and run `python3 plan_test.py`.
If it earns as much as `Plan`, the plan wasn't doing the work. There's no worked answer, because we haven't run it. Pick your
steps before you look at the questions, and five runs of six questions won't settle a close result.

## Common mistakes

- **Reading a plan as evidence.** It looks like thinking. 0 of 30 plans named the band.
- **Scoring only the final answer.** A run can be right with the second fact never seen, so check what it searched.
- **Treating a note as a fact.** "Band E staff must give 8 weeks" was true, and it was the wrong row.
- **Comparing without the cost.** A tie on score at 3.5 times the calls is a loss.
- **Trusting one batch or one run.** Run it again, and don't rank close scores.
- **Using a pattern on every question.** The plain agent did better on the questions that needed one file.
- **Believing "earned" blindly.** It was too harsh on the repair questions, where one file is enough.

## Recap

- `Split` writes every search before it sees a result, so no search can use what the handbook said.
- `Plan` writes up to three steps, then searches each one, rewrites later searches from what's known, and answers from
  the excerpts and the notes. It's 7 model calls for three steps.
- Earned means right, and the searches saw both files. It separates having the facts from getting lucky.
- Over 60 runs each, `Plan` scored 20 strict and 14 earned, and `Split` scored 20 and 16, at 2 calls. That's a tie.
- The setups that left searching to the model searched about once, and earned nothing.
- Many plans were generic. None of the 30 plans for the band questions named the band, and they earned 8 passes anyway.
  So the gain may come from more searching, not smarter planning, and this test can't separate them.
- Carrying facts forward cuts both ways: a one-line note kept "Band E", and a known branch name bent a search away from
  `shifts.md`.
- On direct and unanswerable questions, all four setups scored 36 of 36. `Plan` did no harm, and paid 3.5 times the calls.

**A plan that looks good isn't evidence that planning worked.** Measure the searches, the files and the cost.

## Where this comes from

Asking a model to write a plan before it acts comes from the 2023 paper
[Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091). Searching, reasoning, and using what was found to choose
the next search is studied for multi-step questions in
[Interleaving Retrieval with Chain-of-Thought Reasoning](https://arxiv.org/abs/2212.10509). Both used other models and
other tests, so their results don't carry over to ours. Measure your own.

**Next:** chapter 27, durable execution, keeps a long job safe when it's killed halfway through.
