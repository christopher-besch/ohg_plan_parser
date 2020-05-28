import unittest
import plan_parser
import csv
import os


class TestChange(unittest.TestCase):
    line_pairs = []

    def setUp(self):
        # getting line-translation pairs
        for entry in os.listdir("../test_plans/translated"):
            # get lines from file
            with open(os.path.join("../test_plans/translated", entry), "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file, delimiter=";", quotechar='"')
                for row in csv_reader:
                    if row[1].strip() != "":
                        self.line_pairs.append([row[0], row[1]])

    def test_all(self):
        # test with every line
        for line in self.line_pairs:
            test_change = plan_parser.Change(line[0])
            self.assertEqual(line[1], str(test_change))


if __name__ == '__main__':
    unittest.main()
