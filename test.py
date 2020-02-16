from plan_parser import get_raw

days = get_raw()

for day in days:
    print(day["date"])
    for line in day["text"]:
        print(line)
    print()
    print()
    print()
