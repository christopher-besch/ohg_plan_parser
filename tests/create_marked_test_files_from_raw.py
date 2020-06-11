from plan_parser import scan, get_raw
import os
import json
import sys

if input("Are you sure you want to overwrite existing files?") != "yes":
    sys.exit()

# getting plan pairs from raw
for entry in os.listdir("../test_plans/raw"):
    # raw, directly downloaded
    with open(os.path.join("../test_plans/raw", entry), "r", encoding="utf-8") as file:
        raw = file.read()
        converted_raw = get_raw(raw)
        # doing this for every day in this plan
        marked = []
        for day in converted_raw:
            marked.append(scan(day["text"]))

    with open(os.path.join("../test_plans/marked", entry), "w", encoding="utf-8") as file:
        file.write(json.dumps(marked))
