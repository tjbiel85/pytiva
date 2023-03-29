import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.activity import ActivityDataSet

# local test config
import testconfig


class TestActivityTimeSeries(unittest.TestCase):

    def setUp(self):
        self.df_activity_test_data = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['DS_ACTIVITY']),
            parse_dates=['activity_start', 'activity_end']
        )
        self.ds_activity = ActivityDataSet(self.df_activity_test_data)
        self.ts_concurrency_test_data = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['TS_CONCURRENCY']),
            parse_dates=['timestamp'],
            index_col='timestamp'
        )

    def test_concurrency_generation(self):
        ts_concurrency = self.ds_activity.concurrency_ts()
        self.assertTrue(all(ts_concurrency == self.ts_concurrency_test_data))


# in a script file
if __name__ == '__main__':
    unittest.main()
