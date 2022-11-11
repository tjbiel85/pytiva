import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.staffing import ProviderShift

WD = r'test_data'

OB_SHIFT_DEFINITIONS = [
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

class TestProviderShift(unittest.TestCase):

    def test_provider_shift_instantiation(self):
        dict_provider_shifts = {s['label']: ProviderShift(**s) for s in OB_SHIFT_DEFINITIONS}
        self.assertTrue(all([isinstance(ps, ProviderShift) for ps in dict_provider_shifts.values()]))

    def test_provider_shifts_have_expected_attributes(self):
        expected_ps_attributes = [
            'label',
            'start',
            'duration',
            'end',
            'capacity'
        ]
        dict_provider_shifts = {s['label']: ProviderShift(**s) for s in OB_SHIFT_DEFINITIONS}
        self.assertTrue(
            all([[hasattr(ps, expected) for expected in expected_ps_attributes]
                 for ps in dict_provider_shifts.values()])
        )

# in a script file
if __name__ == '__main__':
    unittest.main()
