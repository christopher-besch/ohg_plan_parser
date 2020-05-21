import unittest
import os
import plan_parser
import itertools
import json


class TestGetRaw(unittest.TestCase):

    test_plans = []

    def setUp(self):
        # getting plan pairs
        for entry in os.listdir("../test_plans/raw"):
            this_entry = {
                "raw": "",
                "converted_raw": ""
            }
            # raw, directly downloaded
            with open(os.path.join("../test_plans/raw", entry), "r", encoding="utf-8") as file:
                this_entry["raw"] = file.read()

            # cut at day breaks
            with open(os.path.join("../test_plans/converted_raw", entry), "r", encoding="utf-8") as file:
                this_entry["converted_raw"] = file.read()

            self.test_plans.append(this_entry)

    # test one file
    def test_from_single_file(self):
        for plan in self.test_plans:
            # test from one pair
            result = plan_parser.get_raw((plan["raw"]))
            required_result = [json.loads(plan["converted_raw"])]

            self.assertEqual(required_result, result)

    # test multiple pairs
    def test_from_multiple_files(self):
        number_tests = 0
        for amount in range(2, len(self.test_plans) + 1):
            pairs = list(itertools.permutations(self.test_plans, r=amount))
            for pair in pairs:
                result = plan_parser.get_raw(("".join([chosen_one["raw"] for chosen_one in pair])))
                required_result = [json.loads(plan["converted_raw"]) for plan in pair]

                self.assertEqual(required_result, result)

                number_tests += 1
                if number_tests >= 10:
                    return

    def test_empty(self):
        result = plan_parser.get_raw("")
        required_result = []

        self.assertEqual(required_result, result)

    def test_garbage(self):
        result = plan_parser.get_raw("UZASGFJGgasuizfg UZGADZUIGZFUG\nhafzuigzu\n")
        required_result = []

        self.assertEqual(required_result, result)
