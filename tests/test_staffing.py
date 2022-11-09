import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.staffing import qgenda_task_grid_to_long_format, ProviderShift

WD = r'test_data'
QGENDA_EXPORT_TEST_DATA_FILENAME = 'CU_Medicine_-_Department_of_Anesthesiology - Grid By Task - 10_1_2021 to 9_30_2022.xlsx'
STAFFING_LONG_FORMAT_COMPARISON_TEST_DATA_FILENAME = 'anesthesia_staffing_data_long.csv'


class TestQgendaWrangling(unittest.TestCase):

    def setUp(self):
        self.df_long_format_reference = pd.read_csv(
            os.path.join(WD, STAFFING_LONG_FORMAT_COMPARISON_TEST_DATA_FILENAME),
        )

    def test_wrangle_qgenda_to_long(self):
        df_long_format_attempt = qgenda_task_grid_to_long_format(os.path.join(WD, QGENDA_EXPORT_TEST_DATA_FILENAME))
        self.assertTrue(all(self.df_long_format_reference == df_long_format_attempt))


# in a script file
if __name__ == '__main__':
    unittest.main()
