"""Six small experiments that show how an LLM works."""
import math

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5:7b"


def chat(messages, **options):
    """Send a conversation to the model, and return its reply as text."""
    body = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    response = requests.post(f"{OLLAMA}/api/chat", json=body, timeout=180)
    response.raise_for_status()
    return response.json()["message"]["content"]


# Two measuring tools. They're provided for you, and you don't need to memorize them.
# They use Ollama's /api/generate, which can show what the model does with raw text.
def measure(text, **extra):
    """Send raw text to the model, and return Ollama's measurements."""
    body = {"model": MODEL, "prompt": text, "raw": True, "stream": False,
            "options": {"num_predict": 1, "temperature": 0}, **extra}
    response = requests.post(f"{OLLAMA}/api/generate", json=body, timeout=180)
    response.raise_for_status()
    return response.json()


def count_tokens(text):
    """Return how many tokens the model reads for this text."""
    return measure(text)["prompt_eval_count"]


def next_token_chances(text):
    """Return the model's top guesses for the next token, with their chances."""
    guesses = measure(text, logprobs=True, top_logprobs=5)["logprobs"][0]["top_logprobs"]
    return [(guess["token"], math.exp(guess["logprob"])) for guess in guesses]


print("1. Tokens")
for text in ["Hello", "Hello world", "unbelievably", "12345678", "नमस्ते दुनिया"]:
    print(f"  {text!r}: characters: {len(text)}, tokens: {count_tokens(text)}")

print("2. Next-token prediction")
for token, chance in next_token_chances("The capital of France is"):
    print(f"  {token!r}: {chance:.1%}")

print("3. Temperature")
prompt = {"role": "user", "content": "Suggest a name for a coffee shop. Reply with only the name."}
for temperature in [0, 0.7, 1.5]:
    names = [chat([prompt], temperature=temperature, seed=seed).strip() for seed in range(6)]
    print(f"  {temperature}: {len(set(names))} different: {names}")

print("4. No memory")
intro = {"role": "user", "content": "My name is Asha. Say hi."}
question = {"role": "user", "content": "What is my name? Reply in one short sentence."}
reply = chat([intro], temperature=0)
print("  Separate call:", chat([question], temperature=0))
print("  With history: ", chat([intro, {"role": "assistant", "content": reply}, question], temperature=0))

print("5. Context window")
filler = " ".join(f"Line {number}: the shop sold coffee and tea." for number in range(60))
message = f"The secret code is 7342.\n{filler}\nWhat is the secret code? Reply with only the code."
for size in [4096, 256]:
    answer = chat([{"role": "user", "content": message}], temperature=0, num_ctx=size, num_predict=30)
    print(f"  Window of {size} tokens: {answer!r}")

print("6. Made-up answers")
paper = "Summarize the paper 'Recursive Tea Embeddings for Quantum Coffee Agents' by Dr. Mira Sundaram."
print(" ", chat([{"role": "user", "content": paper + " Use one sentence."}], temperature=0, num_predict=60))
