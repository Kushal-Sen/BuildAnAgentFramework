"""Talk to the sales agent. It remembers the conversation. Type quit to stop."""
from sales_tools import toolbox
from whitebox import Agent, load_model

agent = Agent(load_model(), toolbox, options={"temperature": 0})
history = None
question = input("You: ")
while question != "quit":
    result = agent.run(question, history)
    history = result.messages
    print("Agent:", result.answer)
    question = input("You: ")
