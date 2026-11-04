# Chapter 07: How LLMs work

**Time:** about 2 hours. **You'll learn:** what's happening inside the model, using six experiments
on your own computer.

## Where we are

In chapter 06, you wrote a `chat` function, and two things happened that needed explaining. The
same question gave different answers, and the model forgot your name. So far, the model has been
a black box. In this chapter, you'll open it and solve both puzzles.

You don't need any math to follow along. Everything here comes from running the code.

## What an LLM is

**LLM** stands for large language model. It's a program trained on a huge amount of text to do one
job: **predict what comes next**.

Inside is a very large set of numbers, called **parameters**. Your model has about 7.6 billion of
them. They were set during **training**, and they don't change when you use the model.

Everything an LLM seems to do, like answering, translating or writing code, comes from that one
job, repeated.

## Run the experiments

[Start Ollama](../00-setup/README.md#step-4-start-ollama), and activate the `.venv` you made in
chapter 05. Before you run anything, read each **Predict** question below and make a guess. Then,
from `chapters/07-how-llms-work/code`, run:

```bash
python3 experiments.py
```

It takes about a minute. This is real output from `qwen2.5:7b`. Some of yours will differ:

```text
1. Tokens
  'Hello': characters: 5, tokens: 1
  'Hello world': characters: 11, tokens: 2
  'unbelievably': characters: 12, tokens: 3
  '12345678': characters: 8, tokens: 8
  'नमस्ते दुनिया': characters: 13, tokens: 13
2. Next-token prediction
  ' Paris': 54.5%
  ' __': 6.9%
  ' a': 4.6%
  ' ______': 4.5%
  ' ____': 4.0%
3. Temperature
  0: 1 different: ['Brew Haven', 'Brew Haven', 'Brew Haven', 'Brew Haven', 'Brew Haven', 'Brew Haven']
  0.7: 5 different: ['Brewed Moments', 'Morning Blend', 'Brewscape', 'Brew Haven', 'Bean Haven', 'Brew Haven']
  1.5: 5 different: ['Café Bliss', 'MorningBlend', 'Brewtopia', 'Brew Haven', 'Mocha Meadows', 'Brew Haven']
4. No memory
  Separate call: You didn't provide your name in the question.
  With history:  Your name is Asha.
5. Context window
  Window of 4096 tokens: '7342'
  Window of 256 tokens: 'coffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeand'
6. Made-up answers
  The paper "Recursive Tea Embeddings for Quantum Coffee Agents" by Dr. Mira Sundaram explores the application of quantum computing principles to develop a novel embedding technique for agents that could potentially optimize decision-making processes in dynamic environments, using a whimsical theme of "coffee" to engage the reader.
```

Open [code/experiments.py](code/experiments.py) and follow along. It uses the same `chat` function
you wrote in chapter 06.

It also has two **measuring tools**, `count_tokens` and `next_token_chances`. They're provided for
you, and you don't need to memorize them. They ask Ollama to report what the model did with some
text, which `chat` can't show.

## 1. Tokens

**Predict:** which of the five texts takes the most tokens?

Models don't read letters or whole words. They read **tokens**, which are small chunks of text.
Each one is stored as a number.

- `Hello` is 1 token.
- `unbelievably` is 3 tokens, because it's a less common word.
- `12345678` is 8 tokens, one for each digit.
- The 13 characters of `नमस्ते दुनिया` take 13 tokens.

For English, a rough rule of thumb is 4 characters per token. Other languages often take more
tokens, and that matters because models have limits measured in tokens, and cloud models usually
charge by the token.

This is also why models can struggle with spelling or counting letters. They don't see the letters.

## 2. Next-token prediction

**Predict:** after "The capital of France is", how sure is the model about the next word?

For any text, the model gives every possible next token a chance. Here are its top guesses after
"The capital of France is":

```text
  ' Paris': 54.5%
  ' __': 6.9%
  ' a': 4.6%
  ' ______': 4.5%
  ' ____': 4.0%
```

The blanks probably reflect fill-in-the-blank text the model saw in training. Either way, it isn't
looking up a fact. It's predicting likely text.

To write a reply, the model repeats one loop:

1. Read all the text so far.
2. Give every possible next token a chance.
3. Pick one.
4. Add it to the text, and repeat.

This is why replies appear piece by piece.

## 3. Temperature

**Predict:** how many different names will each temperature give?

**Temperature** controls how the model picks a token. At 0, it always takes the top choice. Higher
values give less likely tokens a better chance.

We asked for a coffee shop name six times at each temperature:

| Temperature | Different answers |
|---|---|
| 0 | 1 |
| 0.7 | 5 |
| 1.5 | 5 |

**That solves puzzle 1.** In chapter 06, we didn't set a temperature, and the default isn't 0, so
the same question gave different answers.

Use a low temperature when you need consistent results, such as for an agent that calls tools.
Use a higher one for variety. Even at 0, results can differ between machines and model versions.

## 4. No memory

**Predict:** will the separate call know the name?

Each call to the model starts from nothing. It remembered "Asha" only when we sent the earlier
messages again:

```text
  Separate call: You didn't provide your name in the question.
  With history:  Your name is Asha.
```

**That solves puzzle 2.** Your second call in chapter 06 didn't include the first message, so the
model never saw your name.

When a chatbot seems to remember you, the app is resending the conversation each time. You'll write
that code yourself in chapter 12.

## 5. Context window

**Predict:** will the small window still find the code?

The **context window** is the most tokens a model can handle at once, including its reply. We hid a
secret code at the start of a long message, then tried two window sizes:

```text
  Window of 4096 tokens: '7342'
  Window of 256 tokens: 'coffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeandteacoffeeand'
```

With the small window, the text didn't fit, so the secret was lost and the reply was nonsense.
**There was no error message.** Ollama cut the text and carried on.

Agents resend everything on each step, so they can fill the window quickly. You'll manage this in
chapter 23.

## 6. Made-up answers

**Predict:** will the model admit that the paper isn't real?

We asked the model to summarize a paper that doesn't exist, and it did so confidently:

```text
  The paper "Recursive Tea Embeddings for Quantum Coffee Agents" by Dr. Mira Sundaram explores the application of quantum computing principles...
```

This is called **hallucination**. The model predicts likely text, and a real-sounding summary is
likely text. It doesn't check facts. In our test, it did refuse two other made-up questions, so you
can't predict when this will happen.

That's a big reason why agents use tools. A tool can look up the real answer.

## What this means for agents

| What you learned | Why it matters |
|---|---|
| Models predict text | Check their output, and don't trust it blindly |
| Tokens are the unit | Limits and costs are counted in tokens |
| Temperature adds variety | Use a low value for reliable tool use |
| Models have no memory | Your code must keep the conversation |
| Context is limited | Long runs need managing |
| Models make things up | Tools and retrieval give them real facts |

## Exercises

In this chapter's folder, open [exercises.py](exercises.py) and complete the five TODOs:

1. `estimate_tokens`: use the rule of thumb.
2. `most_likely`: pick the top token.
3. `apply_temperature`: see how temperature changes the chances.
4. `fits_window`: check a context limit.
5. `add_turn`: add to a conversation without changing the original.

Then check your work:

```bash
python3 -m pytest test_exercises.py
```

You've finished when you see `5 passed`. Worked answers are in
[solutions/exercises.py](solutions/exercises.py).

## Common mistakes

- Thinking the model looks facts up. It predicts text.
- Thinking the model remembers earlier calls. Your code has to resend them.
- Counting words instead of tokens.
- Expecting an error when the context overflows. You may just get a bad answer.

## Recap

- An LLM predicts the next token, one at a time.
- Tokens are the chunks of text a model reads.
- Temperature controls how much variety you get.
- Each call starts with no memory.
- The context window limits what fits, and overflow can be silent.
- Models can state made-up things confidently.

## Where this comes from

Today's LLMs are built on the Transformer, introduced in the 2017 paper
[Attention Is All You Need](https://arxiv.org/abs/1706.03762). For a visual explanation, see
[The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/).

**Next:** chapter 08, where you'll learn to steer the model with better prompts.
