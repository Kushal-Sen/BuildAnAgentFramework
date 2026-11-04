# Part 0 checkpoint: an order tracker

**Time:** about 45 minutes. This checkpoint uses everything from chapters 01 to 05.

Open [checkpoint.py](checkpoint.py) and complete the five TODOs:

1. `Order`: a dataclass with a `total` method.
2. `load_orders`: read JSON from a file into `Order` objects.
3. `logged`: a decorator that records each call.
4. `big_orders`: a generator that filters orders.
5. `fetch_json`: handle a web response.

Then check your work from this folder:

```bash
python3 -m pytest test_checkpoint.py
```

You've finished Part 0 when you see `5 passed`. Worked answers are in
[solutions/checkpoint.py](solutions/checkpoint.py).
