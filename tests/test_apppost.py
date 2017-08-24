import unittest
import csv
import apppost as app


class apppostTest(unittest.TestCase):

    f = open('tests/data/testdata.csv', 'r')
    reader = csv.reader(f)
    header = next(reader)
    dataset = []
    for row in reader:
        dataset.append(row)
    f.close()

    def test_select_for_object(self):
        db = app.connect_db()
        for row in self.dataset:
            print(row)
            db.execute(
                ("INSERT INTO tasks (end_time,item) VALUES (%s,%s)" % (row[0], row[1])))
        # cur = db.execute("SELECT * FROM tasks")

        # self.assertEqual(a, b)
