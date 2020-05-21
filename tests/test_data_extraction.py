import unittest
import os
import plan_parser
import itertools
import json


class TestGetRaw(unittest.TestCase):

    test_plans = []

    def setUp(self):
        # getting plan pairs
        for entry in os.listdir("../test_plans/converted_raw"):
            this_entry = {}
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
            required_result = json.loads(plan["converted_raw"])

            self.assertEqual(required_result, result)

    # test multiple pairs
    def test_from_multiple_files(self):
        number_tests = 0
        for amount in range(2, len(self.test_plans) + 1):
            pairs = list(itertools.permutations(self.test_plans, r=amount))
            for pair in pairs:
                result = plan_parser.get_raw(("".join([chosen_one["raw"] for chosen_one in pair])))
                days_sum = []
                for day in pair:
                    days_sum += json.loads(day["converted_raw"])

                required_result = days_sum

                self.assertEqual(required_result, result)

                number_tests += 1
                if number_tests >= 100:
                    return

    def test_empty(self):
        result = plan_parser.get_raw("")
        required_result = []

        self.assertEqual(required_result, result)

    def test_garbage(self):
        result = plan_parser.get_raw("UZASGFJGgasuizfg UZGADZUIGZFUG\nhafzuigzu\n")
        required_result = []

        self.assertEqual(required_result, result)


class TestFindStart(unittest.TestCase):

    raw_test_plans = {}

    def setUp(self):
        # getting raw plans
        for entry in os.listdir("../test_plans/converted_raw"):
            # raw, directly downloaded
            with open(os.path.join("../test_plans/raw", entry), "r", encoding="utf-8") as file:
                self.raw_test_plans[entry] = file.read()

    def test_2018_08_09(self):
        result = plan_parser.find_start(self.raw_test_plans["2018_08_09.txt"].split("\n"))
        print(result)
        required_result = 1
        self.assertEqual(required_result, result)

    def test_empty(self):
        result = plan_parser.find_start([])
        required_result = None
        self.assertEqual(required_result, result)


class TestScan(unittest.TestCase):

    test_plans = []

    def setUp(self):
        # getting plan pairs
        for entry in os.listdir("../test_plans/marked"):
            this_entry = {}
            # cut at day breaks
            with open(os.path.join("../test_plans/converted_raw", entry), "r", encoding="utf-8") as file:
                this_entry["converted_raw"] = file.read()

            # marked
            with open(os.path.join("../test_plans/marked", entry), "r", encoding="utf-8") as file:
                this_entry["intel"] = file.read()

            self.test_plans.append(this_entry)

    def test_from_single_file(self):
        for plan in self.test_plans:
            # test each day from one pair
            result = []
            for day in json.loads(plan["converted_raw"]):
                result.append(plan_parser.scan(day["text"]))
            required_result = json.loads(plan["intel"])

            self.assertEqual(required_result, result)


if __name__ == "__main":
    unittest.main()
