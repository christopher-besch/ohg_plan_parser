from plan_parser import get_raw, get_intel, Change
import datetime

# get raw data from iserv
days = get_raw()

# groups the user is a part of
groups = ["10.3",
          "Jahrgang 6"]

# going through every day
for day in days:
    # get date
    date = datetime.date.fromisoformat(day["date"])

    # extract valuable data
    intel = get_intel(day["text"], groups)

    # print intel
    print(intel["new_day"])
    print(intel["pressure"])
    print()
    for line in intel["text"]:
        print(line)

    print()
    for line in intel["groups_intel"]:
        change_obj = Change(line, date.weekday(), date.year)
        print(change_obj)

    print()
    print()
    print()
