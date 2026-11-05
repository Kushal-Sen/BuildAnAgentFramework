"""Keep a record of the run in a file, then read it back."""
from sales_tools import toolbox
from whitebox import Agent, Tracer, load_model, show_trace

QUESTION = "Which day had the most coffee revenue?"

agent = Agent(load_model(), toolbox, options={"temperature": 0}, hooks=[Tracer("trace.jsonl")])
agent.run(QUESTION)
show_trace("trace.jsonl")
