"""Read the plans: python3 plan_plans.py for counts, or python3 plan_plans.py lead-notice for one question."""
import sys

from hop_setups import saved_tests

runs = [run for run in saved_tests() if run["setup"] == "Plan"]
BAND_QUESTIONS = ["senior-beans", "shift-lead-pay", "lead-notice"]


def names_word(run, *words):
    return any(word in step.lower() for step in run["plan"] for word in words)


def earned(run):
    return run["strict"] and run["both_files"]


if sys.argv[1:]:
    for run in runs:
        if run["name"] == sys.argv[1]:
            print("earned" if earned(run) else "pass" if run["strict"] else "FAIL")
            for step in run["plan"]:
                print("   ", step[:90])
else:
    band = [run for run in runs if run["name"] in BAND_QUESTIONS]
    harbour = [run for run in runs if run["name"] == "harbour-arrive"]
    print(f"Plans in all: {len(runs)}")
    print(f"Mention the handbook, a section or a policy: {sum(names_word(run, 'handbook', 'section', 'policy') for run in runs)}")
    print(f"Three questions that turn on a band: {len(band)} plans")
    print(f"  name the band: {sum(names_word(run, 'band') for run in band)}")
    print(f"  earned anyway: {sum(earned(run) for run in band)}")
    print(f"harbour-arrive: {len(harbour)} plans")
    print(f"  name the arrival time: {sum(names_word(run, 'arrival', 'arrive') for run in harbour)}")
    print(f"  earned: {sum(earned(run) for run in harbour)}")
