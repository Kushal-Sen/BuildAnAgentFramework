"""Print the hop test: python3 plan_scores.py, or add batches or questions."""
import sys

from hop_setups import TWO_FILES, load_runs, saved_tests


def strict(rows):
    return sum(row["strict"] for row in rows)


def earned(rows):
    return sum(row["strict"] and row["both_files"] for row in rows)


def of(rows, setup, name=None):
    return [row for row in rows if row["setup"] == setup and name in (None, row["name"])]


runs = saved_tests()
setups = list(dict.fromkeys(run["setup"] for run in runs))
names = list(dict.fromkeys(run["name"] for run in runs))


def show_totals():
    print(f"{'Setup':<14}{'Strict':>7}{'Earned':>8}{'Calls':>7}{'Searches':>10}{'Calls per earned':>18}")
    for setup in setups:
        rows = of(runs, setup)
        calls = sum(row["calls"] for row in rows)
        searches = sum(len(row["queries"]) for row in rows)
        each = f"{calls / earned(rows):.1f}" if earned(rows) else "-"
        print(f"{setup:<14}{strict(rows):>7}{earned(rows):>8}{calls / len(rows):>7.1f}"
              f"{searches / len(rows):>10.1f}{each:>18}")
    print(f"{len(rows)} runs each. Calls and Searches are per run.")


def show_batches():
    first, again = load_runs("plan-test.json"), load_runs("plan-test-again.json")
    print(f"{'Setup':<14}{'Strict':>12}{'Earned':>12}   (first batch, second batch, 30 runs each)")
    for setup in setups:
        one, two = of(first, setup), of(again, setup)
        print(f"{setup:<14}{strict(one):>8}, {strict(two):>2}{earned(one):>9}, {earned(two):>2}")


def show_questions():
    print("Strict / earned, out of 10 runs")
    print(f"{'Question':<18}" + "".join(f"{setup:>14}" for setup in setups))
    for name in names:
        cells = [f"{strict(of(runs, setup, name))} / {earned(of(runs, setup, name))}" for setup in setups]
        print(f"{name:<18}" + "".join(f"{cell:>14}" for cell in cells))
    two_files = [row for row in runs if row["name"] in TWO_FILES]
    cells = [f"{strict(of(two_files, setup))} / {earned(of(two_files, setup))}" for setup in setups]
    print(f"{'Needs both, of 40':<18}" + "".join(f"{cell:>14}" for cell in cells))


{"batches": show_batches, "questions": show_questions}.get("".join(sys.argv[1:]), show_totals)()
