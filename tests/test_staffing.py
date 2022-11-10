import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.staffing import qgenda_task_grid_to_long_format, ProviderShift, staff_activity_from_assignments_long_format

WD = r'test_data'
QGENDA_EXPORT_TEST_DATA_FILENAME = 'CU_Medicine_-_Department_of_Anesthesiology - Grid By Task - 10_1_2021 to 9_30_2022.xlsx'
STAFFING_LONG_FORMAT_COMPARISON_TEST_DATA_FILENAME = 'anesthesia_staffing_data_long.csv'
STAFFING_ACTIVITY_REFERENCE_DATA = 'staffing_activity_dataset_test_reference.csv'


class TestQgendaWrangling(unittest.TestCase):

    def setUp(self):
        self.df_long_format_reference = pd.read_csv(
            os.path.join(WD, STAFFING_LONG_FORMAT_COMPARISON_TEST_DATA_FILENAME),
            parse_dates = ['date']
        )

    def test_wrangle_qgenda_to_long(self):
        df_long_format_attempt = qgenda_task_grid_to_long_format(os.path.join(WD, QGENDA_EXPORT_TEST_DATA_FILENAME))
        self.assertTrue(all(self.df_long_format_reference == df_long_format_attempt))

    def test_shifts_from_qgenda_long(self):
        ob_assignments = [
            'OB',  # attending(s)
            'OB Fellow',  # fellow(s)
            'APP-OB', 'APP-OBa', 'APP-OBp',  # APP
            'Res-OBA', 'Res-OBA Short', 'Res-OBP'  # residents
        ]

        data_ob_only = self.df_long_format_reference[self.df_long_format_reference['assignment'].isin(ob_assignments)]

        ob_shift_definitions = [
            {
                'label': 'OB',
                'start': pd.to_timedelta(7, unit='hour'),
                'duration': pd.to_timedelta(8, unit='hour'),
                'capacity': 0
            },

            {
                'label': 'OB Fellow',
                'start': pd.to_timedelta(7, unit='hour'),
                'duration': pd.to_timedelta(10, unit='hour'),
                'capacity': 0
            },

            {
                'label': 'APP-OB',
                'start': pd.to_timedelta(7, unit='hour'),
                'duration': pd.to_timedelta(24, unit='hour'),
                'capacity': 1
            },

            {
                'label': 'APP-OBa',
                'start': pd.to_timedelta(7, unit='hour'),
                'duration': pd.to_timedelta(12, unit='hour'),
                'capacity': 1
            },

            {
                'label': 'APP-OBp',
                'start': pd.to_timedelta(19, unit='hour'),
                'duration': pd.to_timedelta(12, unit='hour'),
                'capacity': 1
            },

            {
                'label': 'Res-OBA Short',
                'start': pd.to_timedelta(7, unit='hour'),
                'duration': pd.to_timedelta(8, unit='hour'),
                'capacity': 1
            },

            {
                'label': 'Res-OBA',
                'start': pd.to_timedelta(6, unit='hour'),
                'duration': pd.to_timedelta(12, unit='hour'),
                'capacity': 1
            },

            {
                'label': 'Res-OBP',
                'start': pd.to_timedelta(18, unit='hour'),
                'duration': pd.to_timedelta(12, unit='hour'),
                'capacity': 1
            }
        ]

        dict_provider_shifts = {s['label']: ProviderShift(**s) for s in ob_shift_definitions}

        ds_staffing = staff_activity_from_assignments_long_format(
            data_ob_only,
            dict_provider_shifts
        )

        df_staffing_reference = pd.read_csv(os.path.join(WD, STAFFING_ACTIVITY_REFERENCE_DATA))
        self.assertTrue(all(df_staffing_reference == ds_staffing.df))

# in a script file
if __name__ == '__main__':
    unittest.main()
