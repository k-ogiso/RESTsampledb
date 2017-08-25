import os
import flaskr
import unittest
import tempfileimport
import csv
import apppost as flaskr


class apppostTest(unittest.TestCase):

    # test data setup
    f = open('tests/data/testdata.csv', 'r')
    reader = csv.reader(f)
    header = next(reader)
    dataset = []

    for row in reader:
        dataset.append(row)
    f.close()

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_select_for_object(self):
        #
        db = app.connect_db()
        db.execute("DELETE FROM tasks")
        for row in self.dataset:
            db.execute(
                ("INSERT INTO tasks (end_date,item) VALUES ('%s','%s')" % (row[0], row[1])))
        dbcount = db.execute("SELECT COUNT(*) FROM tasks").fetchall()[0][0]
        print(app.get_tasks())
        self.assertEqual("a", "b")


if __name__ == '__main__':
    unittest.main()
