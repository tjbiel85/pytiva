import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.anesthesia import AnesthesiaCaseDataSet

WD = r'test_data'
ACTIVITY_TEST_DATA_FILENAME = 'activity_test_data_full.csv'
TEST_DATA_COLUMN_MAP_TO_VALID_CASE_DATA = {
    'activity_start': 'anesthesia_start',
    'activity_end': 'anesthesia_end',
    'patient': 'case_id',
    'activity': 'procedure'
}

# todo: enforce anesthesia start and end columns are datetime-able

class TestAnesthesiaCaseDataSet(unittest.TestCase):
    def setUp(self):
        self.df_ref = pd.read_csv(
            os.path.join(WD, ACTIVITY_TEST_DATA_FILENAME),
            #parse_dates=['activity_start', 'activity_end']
        )

    def test_case_ds_missing_required_columns_raises_exception(self):
        # the default activity test data set doesn't have columns appropriate for an anesthesia case data set
        with self.assertRaises(Exception):
            ads = AnesthesiaCaseDataSet(self.df_ref)

    def test_create_case_ds_after_mapping_appropriate_columns(self):
        ads = AnesthesiaCaseDataSet(self.df_ref.rename(columns=TEST_DATA_COLUMN_MAP_TO_VALID_CASE_DATA))
        self.assertTrue(isinstance(ads, AnesthesiaCaseDataSet))


# in a script file
if __name__ == '__main__':
    unittest.main()
