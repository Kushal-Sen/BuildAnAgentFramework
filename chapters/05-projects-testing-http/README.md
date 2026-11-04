# Chapter 05: Virtual environments, packages, pytest and HTTP

**Time:** about 1.5 hours. **You'll learn:** how to set up a real project, test it, and talk to a
web service.

## Where we are

In chapter 04, you finished the core Python features. So far, each program has been a single
file using only what comes with Python. Real projects use other people's code, have automated
tests, and talk to other services. Your agent will do all three.

[Start Ollama](../00-setup/README.md#step-4-start-ollama) before you begin.

## Virtual environments

A **package** is code someone else wrote that you can install. A **virtual environment** is a
private folder of packages for one project, so projects don't interfere with each other.

From the course folder, create one and turn it on:

```bash
# macOS and Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

Your prompt now starts with `(.venv)`, which shows it's on. You only create it once, but you
need to activate it each time you open a new terminal. Run `deactivate` to turn it off.

## Installing packages

**pip** installs packages. A `requirements.txt` file lists what a project needs:

```text
pytest
requests
```

Go to `chapters/05-projects-testing-http/code`, then install them:

```bash
python3 -m pip install -r requirements.txt
```

The real output ends like this. `pytest` and `requests` also brought along the packages they need:

```text
Successfully installed certifi-2026.10.23 charset_normalizer-3.5.2 idna-3.20 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.2.0 requests-2.34.2 urllib3-2.8.0
```

Your version numbers may be different.

## Modules and packages of your own

A Python file is a **module**. A folder of modules with an `__init__.py` file is a package.
Open [code/shop/prices.py](code/shop/prices.py), then see how
[code/main.py](code/main.py) uses it:

```python
from shop.prices import order_total
```

## Testing with pytest

A **test** is code that checks your code. Instead of checking results by eye, you write down what
should happen, and run every test with one command.

```python
from shop.prices import discounted, order_total


def test_order_total():
    assert order_total(120, 2) == 240


def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError):
        order_total(120, -1)
```

- pytest runs every function whose name starts with `test_`, in files named `test_*.py`.
- `assert` checks that something is true.
- `pytest.raises` checks that an error happens.

From the `code` folder, run:

```bash
python3 -m pytest
```

```text
collected 3 items

tests/test_prices.py ...                                                 [100%]

============================== 3 passed ===============================
```

Each `.` is a passing test. When one fails, pytest shows what it expected and what it got:

```text
>       assert total(120, 2) == 240
E       assert 122 == 240
E        +  where 122 = total(120, 2)
```

This function added the numbers when it should have multiplied them.

## HTTP

**HTTP** is how programs talk over a network. A client sends a **request**, and a server sends
back a **response**. Ollama runs a small web server on your computer, and every model call in
this course uses HTTP.

A request has a **URL** and a **method**. `GET` asks for data, and `POST` sends data. A response
has a **status code**:

| Code | Meaning |
|---|---|
| 200 | It worked |
| 404 | It wasn't found |
| 429 | Too many requests |
| 500 | The server had a problem |

The `requests` package makes this simple:

```python
response = requests.get(f"{OLLAMA}/api/version", timeout=5)
print(response.status_code, response.json())

response = requests.post(f"{OLLAMA}/api/show", json={"model": "qwen2.5:7b"}, timeout=30)
print(response.status_code, response.json()["details"]["parameter_size"])
```

`json=` turns your dictionary into JSON and sends it. `response.json()` turns the reply into
Python data. Always set a `timeout`, or a stuck server can hang your program forever.

Run it from the `code` folder:

```bash
python3 main.py
```

```text
240
200 {'version': '0.34.4'}
200 7.6B
404 {'error': "model 'no-such-model:latest' not found"}
```

The last line is a real failure, and no Python error was raised. A 404 is still a response, so
always check the status code.

## Reading errors

These are real error messages:

| What happened | What Python says | The fix |
|---|---|---|
| The environment isn't active | `ModuleNotFoundError: No module named 'requests'` | Activate `.venv`, then install |
| pytest isn't installed | `No module named pytest` | Activate `.venv`, then install |
| You're in the wrong folder | `ModuleNotFoundError: No module named 'shop'` | Run it from the `code` folder |
| The server isn't running | `requests.exceptions.ConnectionError: HTTPConnectionPool(...)` | [Start Ollama](../00-setup/README.md#step-4-start-ollama) |
| The reply isn't JSON | `requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` | Check the status code and URL |

## Exercises

From now on, you'll check your work with pytest. In this chapter's folder, open
[exercises.py](exercises.py) and complete TODOs 1 to 4:

1. `read_response`: handle a status code.
2. `fetch_version`: make a GET request.
3. `send_json`: make a POST request.
4. `checked_quantity`: raise an error.

Then open [test_mine.py](test_mine.py) and complete TODO 5 by writing your own test.

Your functions receive `get` and `post` as parameters. Passing them in lets the tests use fake
versions, so they run without a network. You'll use this same trick with a fake model in chapter 13.

Then check your work:

```bash
python3 -m pytest test_exercises.py test_mine.py
```

You've finished when you see `5 passed`. Worked answers are in [solutions/](solutions/).

## Part 0 checkpoint

You've finished the Python primer. Before moving on, complete the
[Part 0 checkpoint](../../checkpoints/part-0/README.md), a small order tracker that uses everything
from chapters 01 to 05.

## Common mistakes

- Forgetting to activate `.venv` in a new terminal.
- Sharing `.venv` or committing it. Share `requirements.txt` instead.
- Leaving out `timeout`.
- Assuming a response means success. Check the status code.

## Recap

- A virtual environment keeps each project's packages separate.
- `requirements.txt` lists what a project needs.
- pytest runs your tests with one command.
- HTTP requests have a URL and a method, and responses have a status code.

## Where this comes from

Tim Berners-Lee created HTTP for the World Wide Web around 1990. To learn more, see the
[pytest documentation](https://docs.pytest.org/) and the
[Requests documentation](https://requests.readthedocs.io/).

**Next:** chapter 06, where you'll learn how LLMs work.
