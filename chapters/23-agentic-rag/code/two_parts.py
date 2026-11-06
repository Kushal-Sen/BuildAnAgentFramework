"""Does the agent look up the band? Ask the same thing two ways, five runs each."""
from library import all_documents, build_agent, build_index, files_seen, searches, tool_text
from questions import strict_pass
from whitebox import load_model

QUESTIONS = [
    "I'm a shift lead. How much notice must I give when I resign?",
    "What band is a shift lead, and how much notice must that band give when they resign?",
]

agent = build_agent(load_model(), build_index(all_documents(), 60))

for question in QUESTIONS:
    print(question)
    for run in range(5):
        result = agent.run(question)
        files = files_seen(tool_text(result))
        both = "pay-bands.md" in files and "resignation.md" in files
        says_four = strict_pass(result.answer, "lead-notice")
        print(f"  searches {len(searches(result))}  both files {both!s:<5}  only 4 weeks {says_four!s:<5}  {searches(result)}")
