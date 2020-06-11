from plan_parser import get_raw
import os
import json
import sys

if input("Are you sure you want to overwrite existing files?") != "yes":
    sys.exit()

# getting plan pairs
for entry in os.listdir("../test_plans/raw"):
    # raw, directly downloaded
    with open(os.path.join("../test_plans/raw", entry), "r", encoding="utf-8") as file:
        vp_raw = file.read()
        converted_raw = get_raw(vp_raw=vp_raw)

    with open(os.path.join("../test_plans/converted_raw", entry), "w", encoding="utf-8") as file:
        file.write(json.dumps(converted_raw))
