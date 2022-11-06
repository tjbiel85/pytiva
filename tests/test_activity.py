import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.activity import ActivityDataset

WD = r'test_data'
ACTIVITY_TEST_DATA_FILENAME = 'activity_test_data_full.csv'
CONCURRENCY_TEST_DATA_FILENAME = 'test_data_concurrency.csv'


class TestActivityTimeSeries(unittest.TestCase):

    def setUp(self):
        self.df_activity_test_data = pd.read_csv(
            os.path.join(WD, ACTIVITY_TEST_DATA_FILENAME),
            parse_dates=['activity_start', 'activity_end']
        )
        self.ds_activity = ActivityDataset(self.df_activity_test_data)
        self.ts_concurrency_test_data = pd.read_csv(
            os.path.join(WD, CONCURRENCY_TEST_DATA_FILENAME),
            parse_dates=['timestamp'],
            index_col='timestamp'
        )

    def test_concurrency_generation(self):
        ts_concurrency = self.ds_activity.concurrency_ts()
        self.assertTrue(all(ts_concurrency == self.ts_concurrency_test_data))


# in a script file
if __name__ == '__main__':
    unittest.main()
