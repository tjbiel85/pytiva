import unittest

# local module to be tested
from pytiva.staffing import ProviderShift

# local test config
import testconfig


class TestProviderShift(unittest.TestCase):
    def test_provider_shift_instantiation(self):
        dict_provider_shifts = {s['label']: ProviderShift(**s) for s in testconfig.STAFF_SHIFT_DEFINITIONS}
        self.assertTrue(all([isinstance(ps, ProviderShift) for ps in dict_provider_shifts.values()]))

    def test_provider_shifts_have_expected_attributes(self):
        expected_ps_attributes = [
            'label',
            'start',
            'duration',
            'end',
            'capacity'
        ]
        dict_provider_shifts = {s['label']: ProviderShift(**s) for s in testconfig.STAFF_SHIFT_DEFINITIONS}
        self.assertTrue(
            all([[hasattr(ps, expected) for expected in expected_ps_attributes]
                 for ps in dict_provider_shifts.values()])
        )

# in a script file
if __name__ == '__main__':
    unittest.main()
