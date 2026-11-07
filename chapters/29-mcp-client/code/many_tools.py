"""Does a bigger menu cost anything? 20 questions, 3 tries each, with 5 to 40 tools, and short or long descriptions."""
import json
import random
from pathlib import Path

from whitebox import Message, RescueToolCalls, Tool, load_model

TARGETS = {
    "get_rota": ("Look up a staff member's rota.", ["When am I working next week?", "What shifts have I got on Saturday?",
                                                    "Show me my rota.", "Am I on the opening shift tomorrow?"]),
    "log_waste": ("Record food or drink thrown away.", ["Two croissants went in the bin, please record it.", "Log three spoiled milks.",
                                                        "We binned a tray of flapjacks.", "Write off six stale muffins."]),
    "check_allergens": ("Say which allergens a menu item contains.", ["Does the banana bread have nuts?", "Is there gluten in the granola?",
                                                                      "Which allergens are in the flapjack?", "Can a coeliac eat the brownie?"]),
    "book_leave": ("Book annual leave for a staff member.", ["Put me down for holiday next Friday.", "I'd like the 3rd to the 7th off.",
                                                             "Book me a week of leave in May.", "Request two days off in June."]),
    "report_fault": ("Report broken equipment to the contractor.", ["The grinder has stopped working.", "The dishwasher is leaking.",
                                                                     "Espresso machine is showing an error.", "The fridge door won't shut."]),
}
OTHER = ["open_till", "close_till", "count_float", "order_beans", "order_milk", "order_cups", "print_labels", "clean_steam_wand",
         "start_cupping", "add_loyalty_stamp", "refund_order", "swap_shift", "check_payslip", "update_address", "reset_password",
         "log_incident", "log_temperature", "check_delivery", "find_lost_property", "update_menu", "book_training", "record_sickness",
         "send_rota_reminder", "check_stock", "calculate_tips", "report_complaint", "add_new_starter", "read_notice_board",
         "check_opening_hours", "contact_area_manager", "book_contractor", "check_uniform_stock", "record_cash_drop", "find_form",
         "check_pay_band"]
PADDING = (" This tool is part of the Quillon staff system, and it works the same way at every branch. The details field takes plain "
           "text, in the staff member's own words. The system records who made each request and when, and it replies with a short "
           "confirmation, or with an error that says what was wrong. Requests are kept for twelve months, and an area manager can read "
           "them later. The service runs during branch opening hours, on the till and on the back office computer, and any changes "
           "made through it appear on the staff noticeboard the next morning.")
SYSTEM = "You help Quillon Coffee staff. Use a tool."
SCHEMA = {"type": "object", "properties": {"details": {"type": "string", "description": "The details"}}, "required": ["details"]}


def menu(size, padding):
    """The five tools that can be right, plus enough others, in a shuffled order that's the same on every run."""
    described = {name: description for name, (description, _) in TARGETS.items()}
    described |= {name: name.replace("_", " ").capitalize() + "." for name in OTHER[:size - 5]}
    tools = [Tool(name, description + padding, SCHEMA, lambda details: "Done.") for name, description in described.items()]
    random.Random(size).shuffle(tools)
    return tools


def measure(model, label, size, padding, options):
    tools = menu(size, padding)
    right = wrong = none = empty = read = 0
    said = []
    for target, (_, questions) in TARGETS.items():
        for question in questions:
            for _ in range(3):
                messages = [Message("system", SYSTEM), Message("user", question)]
                reply = model.chat(messages, tools, temperature=0.7, **options)
                read = reply.tokens_in
                chosen = [call.name for call in reply.tool_calls][:1]
                right += chosen == [target]
                wrong += bool(chosen) and chosen != [target]
                if not chosen and reply.content.strip():
                    none += 1
                    said.append({"question": question, "reply": reply.content})
                empty += not chosen and not reply.content.strip()
    row = {"descriptions": label, "tools": size, "window": options.get("num_ctx", "default"), "right": right, "wrong": wrong,
           "none": none, "empty": empty, "tries": 60, "tokens_in": read, "said": said}
    print(f"{label:<6} {size:>5} {row['window']!s:>8} {right:>6} {wrong:>6} {none:>5} {empty:>6} {read:>8,}", flush=True)
    return row


model = RescueToolCalls(load_model())
print(f"{'Text':<6} {'Tools':>5} {'Window':>8} {'Right':>6} {'Wrong':>6} {'None':>5} {'Empty':>6} {'Read':>8}", flush=True)
rows = [measure(model, "short", size, "", {}) for size in (5, 10, 20, 40)]
rows += [measure(model, "long", size, PADDING, {}) for size in (5, 10, 20, 40)]
rows.append(measure(model, "long", 40, PADDING, {"num_ctx": 16384}))
Path("many_tools.json").write_text(json.dumps(rows, indent=1))
