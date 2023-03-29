import unittest
import os
import pandas as pd

# local module to be tested
import pytiva
from pytiva.staffing import ProviderShift, staff_activity_from_assignments_long_format

# local test config
import testconfig


class TestQgendaWrangling(unittest.TestCase):

    def setUp(self):
        self.df_long_format_reference = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['STAFFING_LONG']),
            parse_dates = ['date']
        )

    def test_shifts_from_long(self):
        dict_provider_shifts = {s['label']: ProviderShift(**s) for s in testconfig.STAFF_SHIFT_DEFINITIONS}

        ds_staffing = staff_activity_from_assignments_long_format(
            self.df_long_format_reference.loc[ self.df_long_format_reference['assignment'].isin(dict_provider_shifts.keys()) ],
            dict_provider_shifts
        )

        df_staffing_reference = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DS_STAFFING_ACTIVITY']))
        ds_staffing_reference = pytiva.ActivityDataSet(df_staffing_reference)

        self.assertTrue(all(ds_staffing_reference._df == ds_staffing._df))

# in a script file
if __name__ == '__main__':
    unittest.main()
