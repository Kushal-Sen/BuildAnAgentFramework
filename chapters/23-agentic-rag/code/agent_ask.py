"""The same question, but the agent chooses what to search for, and when to stop."""
from library import all_documents, build_agent, build_index, files_seen, searches, tool_text
from whitebox import load_model

QUESTION = "I'm a shift lead. How much notice must I give when I resign?"

index = build_index(all_documents(), 60)
agent = build_agent(load_model(), index)

result = agent.run(QUESTION)
for number, query in enumerate(searches(result), start=1):
    print(f"search {number}: {query}")
print("Files seen:", ", ".join(files_seen(tool_text(result))))
print("Answer:", result.answer)
print("Model calls:", result.steps)
