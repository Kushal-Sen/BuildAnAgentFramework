"""Run the sales agent. usage: python3 demo.py [provider/name]"""
import sys

from sales_tools import SCHEMAS, TOOLS
from whitebox import load_model, run_agent

QUESTION = "What was the total coffee revenue across all the days in the sales folder?"

if __name__ == "__main__":
    model = load_model(sys.argv[1] if len(sys.argv) > 1 else None)
    print(run_agent(QUESTION, model, TOOLS, SCHEMAS, temperature=0))
