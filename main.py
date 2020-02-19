from plan_parser import get_raw, get_intel

# get raw data from iserv
days = get_raw()

# groups the user is a part of
groups = ["6.4",
          "Jahrgang 6"]

# going threw every day
for day in days:
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
        print(line)

    print()
    print()
    print()
