import unittest
import os
import pandas as pd

# local module to be tested
import pytiva
from pytiva.staffing import ProviderShift, provider_shift_defs_to_kv_dict, ResourceAssignmentDataSet

# local test config
import testconfig


def check_all_ds_df_vs_comp(x, y):
    return all((x._df.reset_index(drop=True) == y))


class TestResourceAssignmentDataSet(unittest.TestCase):
    def setUp(self):
        self.df_staffing_data_long = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['STAFFING_LONG']),
            parse_dates=['date']
        )
        self.ps_dictionary = provider_shift_defs_to_kv_dict(testconfig.STAFF_SHIFT_DEFINITIONS)

    def test_instantiate_resource_assignment_dataset(self):
        ds_resources = pytiva.staffing.ResourceAssignmentDataSet(self.df_staffing_data_long)
        self.assertIsInstance(ds_resources, ResourceAssignmentDataSet)

    def test_limit_by_ps_dict(self):
        ds_resources = pytiva.staffing.ResourceAssignmentDataSet(self.df_staffing_data_long)
        ds_resources.limit_to_ps_in_dict(self.ps_dictionary)
        comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DS_RESOURCES_LIMITED_BY_PS_DICT']))
        self.assertTrue(check_all_ds_df_vs_comp(ds_resources, comp))

    def test_limit_by_date_list(self):
        ds_resources = pytiva.staffing.ResourceAssignmentDataSet(self.df_staffing_data_long)
        dt_start = pd.to_datetime('2021-10-01')
        dt_end = pd.to_datetime('2021-12-31')
        ds_resources.limit_by_list('date', pd.date_range(start=dt_start, end=dt_end, freq='D'))
        comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DS_RESOURCES_LIMITED_BY_DATE_LIST']))
        self.assertTrue(check_all_ds_df_vs_comp(ds_resources, comp))

    def test_limit_by_date_list_and_ps_dict(self):
        ds_resources = pytiva.staffing.ResourceAssignmentDataSet(self.df_staffing_data_long)
        dt_start = pd.to_datetime('2021-10-01')
        dt_end = pd.to_datetime('2021-12-31')
        ds_resources.limit_by_list('date', pd.date_range(start=dt_start, end=dt_end, freq='D'))
        ds_resources.limit_to_ps_in_dict(self.ps_dictionary)
        comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DS_RESOURCES_LIMITED_BY_DATE_LIST_AND_PS_DICT']))
        self.assertTrue(check_all_ds_df_vs_comp(ds_resources, comp))

    def test_generate_activity_from_ps_dict(self):
        ds_resources = ResourceAssignmentDataSet(
            pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DS_RESOURCES_LIMITED_BY_PS_DICT']))
        )
        ds_resources.limit_by_list('assignment', self.ps_dictionary.keys())
        ads_resources = ds_resources.generate_activity_from_ps_dict(self.ps_dictionary)
        comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['ADS_GENERATE_RESOURCE_ACTIVITY_W_PS_DICT']))
        self.assertTrue(check_all_ds_df_vs_comp(ads_resources, comp))

    def test_generate_capacity_no_params(self):
        ds_resources = pytiva.staffing.ResourceAssignmentDataSet(self.df_staffing_data_long)
        ds_resources.limit_by_list('assignment', self.ps_dictionary.keys())
        self.assertIsInstance(ds_resources, ResourceAssignmentDataSet)


# in a script file
if __name__ == '__main__':
    unittest.main()
