"""Try the checks on answers we wrote ourselves. No model is needed."""
from whitebox import contains, excludes
from whitebox.agent import Result

check = contains("380")
answers = ["The total is 380.", "The total is $1,380.", "The total is 3800.", "Three hundred and eighty."]
for answer in answers:
    print(f"{check.test(Result(answer, [], 1))!s:5}  {answer}")

check = excludes("120")
for answer in ["There's no Friday file, so I can't say.", "No Friday file. Monday was 120."]:
    print(f"{check.test(Result(answer, [], 1))!s:5}  {answer}")
