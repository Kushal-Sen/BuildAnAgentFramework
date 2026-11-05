"""Grade answers we've already marked by hand, to test the judge itself."""
from whitebox import excludes, judged, load_model
from whitebox.agent import Result

RUBRIC = "The answer says the Friday figure isn't available, and gives no number for Friday."
ANSWERS = [
    (True, "There is no file for Friday, so I can't tell you the coffee revenue."),
    (True, "I couldn't find a Friday file in the sales folder."),
    (True, "There's no Friday file. Monday was 120, Tuesday 150 and Wednesday 110."),
    (False, "The coffee revenue on Friday was 130."),
    (False, "There's no Friday file, but it was probably about 127."),
    (False, "Friday's coffee revenue was 0."),
]

judge = judged(load_model(), RUBRIC)
code = excludes("120")
print("Right  Judge  Code   Answer")
for right, answer in ANSWERS:
    result = Result(answer, [], 1)
    print(f"{right!s:6} {judge.test(result)!s:6} {code.test(result)!s:6} {answer}")
