import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.anesthesia import AnesthesiaCaseDataSet

# local test config
import testconfig


class TestAnesthesiaCaseDataSet(unittest.TestCase):

    def setUp(self):
        self.df_ref = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['DS_ACTIVITY'])
        )

    def test_case_ds_missing_required_columns_raises_exception(self):
        # the default activity test data set doesn't have columns appropriate for an anesthesia case data set
        with self.assertRaises(Exception):
            ads = AnesthesiaCaseDataSet(self.df_ref)

    def test_create_case_ds_after_mapping_appropriate_columns(self):
        col_map = testconfig.ACTIVITY_COLS_TO_VALID_CASES_COLS_MAP
        ads = AnesthesiaCaseDataSet(self.df_ref.rename(columns=col_map))
        self.assertTrue(isinstance(ads, AnesthesiaCaseDataSet))


# in a script file
if __name__ == '__main__':
    unittest.main()
