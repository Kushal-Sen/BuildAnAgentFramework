"""The same run as traced.py, with one sentence added to the system prompt."""
from sales_tools import toolbox
from whitebox import Agent, Tracer, load_model, show_trace
from whitebox.agent import SYSTEM

QUESTION = "Which day had the most coffee revenue?"
BETTER = SYSTEM + " Files are in the sales folder."

agent = Agent(
    load_model(), toolbox, system=BETTER, options={"temperature": 0}, hooks=[Tracer("trace.jsonl")]
)
agent.run(QUESTION)
show_trace("trace.jsonl")
