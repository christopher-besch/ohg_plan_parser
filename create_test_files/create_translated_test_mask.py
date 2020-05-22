from plan_parser import scan
import csv
import sys
import os
import json

if input("Are you sure you want to overwrite existing files?") != "yes":
    sys.exit()

# getting plan pairs directly from converted_raw
for entry in os.listdir("../test_plans/converted_raw"):
    # raw, directly downloaded
    with open(os.path.join("../test_plans/converted_raw", entry), "r", encoding="utf-8") as file:
        converted_raw = json.loads(file.read())

    final_file = os.path.join("../test_plans/translated", os.path.splitext(entry)[0] + ".csv")

    with open(final_file, "w", encoding="utf-8", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for day in converted_raw:
            marked_day = scan(day["text"])
            for line, mark in zip(day["text"], marked_day):
                if mark not in {"new_day", "blank", "pressure", "text", "class_name", }:
                    csv_writer.writerow((line, ""))

