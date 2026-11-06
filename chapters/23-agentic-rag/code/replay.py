"""Is it the loop, or the query? Give one-shot Rag the exact queries the agent chose. Needs agent60-runs.json."""
from library import OPTIONS, Keep, Remember, all_documents, build_index, load_runs
from questions import HANDBOOK, RECORDS, summary, to_cases
from whitebox import Rag, load_model, run_eval


class AgentQueries:
    """Searches for the agent's first query in place of the question. Each run uses the next saved one."""

    def __init__(self, index, runs):
        self.index = index
        self.queries = {}
        for run in runs:
            self.queries.setdefault(run["question"], []).append(run["searches"][0])

    def search(self, question, k=5):
        return self.index.search(self.queries[question].pop(0), k)


index = Remember(build_index(all_documents(), 60))
runs = load_runs("agent60-runs.json")
keep = Keep(Rag(load_model(), AgentQueries(index, runs), 3, OPTIONS))
report = run_eval(keep, to_cases(HANDBOOK + RECORDS), runs=3, label="replay")
print(summary(report), flush=True)
report.save("replay.json")
keep.save("replay-runs.json")
