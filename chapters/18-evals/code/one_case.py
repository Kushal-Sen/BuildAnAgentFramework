"""One case, run five times by run_eval."""
from sales_tools import toolbox
from whitebox import Agent, Case, contains, finished, load_model, run_eval, used_tool

case = Case(
    "coffee total",
    "What was the total coffee revenue across all the days in the sales folder?",
    [contains("380"), used_tool("add_numbers"), finished()],
)

agent = Agent(load_model(), toolbox, options={"temperature": 0.7})
report = run_eval(agent, [case], runs=5, label="first eval")
print(report.table())
print(report.rows[0].failures)
