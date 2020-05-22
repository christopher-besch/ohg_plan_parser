from plan_parser import get_intel
import os
import json
import sys

if input("Are you sure you want to overwrite existing files?") != "yes":
    sys.exit()

# groups the user is a part of
groups = ["6.4",
          "Jahrgang 6"]

# getting plan pairs directly from converted_raw
for entry in os.listdir("../test_plans/converted_raw"):
    # raw, directly downloaded
    with open(os.path.join("../test_plans/converted_raw", entry), "r", encoding="utf-8") as file:
        converted_raw = file.read()
        # doing this for every day in this plan
        marked = []
        for day in json.loads(converted_raw):
            marked.append(get_intel(day["text"], groups))

    with open(os.path.join("../test_plans/intel_6_4", entry), "w", encoding="utf-8") as file:
        file.write(json.dumps(marked))
