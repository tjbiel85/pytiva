import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.activity import ActivityDataSet
from pytiva.anesthesia import AnesthesiaCaseMedicationsDataSet

WD = r'test_data'
ACTIVITY_TEST_DATA_FILENAME = 'activity_test_data_full.csv'
CONCURRENCY_TEST_DATA_FILENAME = 'test_data_concurrency.csv'
MED_TEST_DATA_FILENAME = 'med_test_data.csv'
UNDUPLICATED_MED_ACTIVITY_BY_CASE_FILENAME = 'ads_fetch_unduplicated_concurrency_out.csv'


class TestActivityTimeSeries(unittest.TestCase):

    def setUp(self):
        self.med_ds = AnesthesiaCaseMedicationsDataSet(
            pd.read_csv(os.path.join(WD, MED_TEST_DATA_FILENAME), parse_dates=['med_datetime'])
        )

        self.unduplicated_med_activity_by_case_df = pd.read_csv(
            os.path.join(WD, UNDUPLICATED_MED_ACTIVITY_BY_CASE_FILENAME),
            parse_dates=['activity_start', 'activity_end']
        )

    def test_stratified_unduplicated_concurrency(self):
        three_minutes = pd.to_timedelta(3, unit='Min')
        ads = self.med_ds.to_activity_dataset(offset_before=three_minutes, offset_after=three_minutes)
        strata_cols = ['case_id']
        big_df = ads.fetch_unduplicated_concurrency(activities=['medication'], strata=strata_cols)

        self.assertTrue(all(big_df == self.unduplicated_med_activity_by_case_df))

    def test_meds_to_activity_dataset(self):
        """
        Test that a meds dataset will be appropriately converted to an activity dataset across a small range of
        time deltas.
        :return:
        """
        for td in (pd.to_timedelta(n, unit='Min') for n in range(-3, 3)):
            test_ads = self.med_ds.to_activity_dataset(offset_before=td, offset_after=td, default_resolution='1s')
            self.assertTrue(all(test_ads['activity_end'] - test_ads['activity_start'] == 2 * td))


# in a script file
if __name__ == '__main__':
    unittest.main()
