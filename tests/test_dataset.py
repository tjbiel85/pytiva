import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.dataset import DataSet

# local test config
import testconfig


class TestDataSet(unittest.TestCase):
    def setUp(self):
        self.df_ref = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['DS_ACTIVITY']),
            parse_dates=['activity_start', 'activity_end']
        )

    def test_none_data_throws_exception(self):
        # None is usually allowed by pandas.DataFrame
        # but not for a DataSet
        with self.assertRaises(Exception):
            ds = DataSet(None)

    def test_invalid_data_throws_exception(self):
        with self.assertRaises(Exception):
            ds = DataSet('this is a string, and will not do')

    def test_ds_subscriptable(self):
        # test that subscripting is passed through to held DataFrame
        comp_df = self.df_ref.dropna() # exclude NaNs and NaTs for this test
        ds = DataSet(comp_df)
        self.assertTrue(all([all(ds[c] == comp_df[c]) for c in comp_df.columns]))

    def test_ds_exposes_df_attributes(self):
        # test that DataFrame attributes can be called through DataSet.
        # It's possible this test will break if DataSet is extended to have collisions with the DataFrame attribute
        # namespace. In that case, the desired behavior will be to access the attribute on DataSet.
        # So, set aside those in this check. We wouldn't expect them to be equal to the attributes on the held DataFrame
        ds = DataSet(self.df_ref)
        self.assertTrue(all([hasattr(ds, a) for a in dir(ds._df) if a not in dir(ds)]))

    def test_ds_attributes_not_sought_on_df(self):
        # test that assigned attributes on DataSet are available on DataSet and NOT accessed on held DataFrame
        # This one is the complement of test_ds_exposes_df_attributes, in a way. Things that do exist on DataSet should
        # be found there, not on the held DataFrame
        ds = DataSet(self.df_ref)

        # skip over the held DataFrame itself--the truth value of a DataFrame is ambiguous, after all
        excluded = ['_df']
        self.assertTrue(all([ds.__getattribute__(a) == getattr(ds, a) for a in dir(ds) if a not in excluded]))

    def test_accepts_and_uses_index_colum(self):
        # test providing an index_column
        index_column = self.df_ref.columns[0]
        ds = DataSet(self.df_ref, index_column=index_column)
        self.assertTrue(ds.index.name == index_column)

    def test_statistical_testing_of_group_means_anova(self):
        self.df_ref['duration'] = (self.df_ref['activity_end'] - self.df_ref['activity_start']).dt.total_seconds()
        ds = DataSet(self.df_ref)
        tgm_result = ds.test_group_means('activity', 'duration')
        self.assertTrue(tgm_result[0] == testconfig.TESTDATA['EXPECTED_ANOVA_DICT'])

    def test_statistical_testing_of_group_means_hsd(self):
        self.df_ref['duration'] = (self.df_ref['activity_end'] - self.df_ref['activity_start']).dt.total_seconds()
        ds = DataSet(self.df_ref)
        tgm_result = ds.test_group_means('activity', 'duration')
        expected_hsd = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['EXPECTED_TUKEY_HSD_DF']))
        self.assertTrue(all(tgm_result[1]['result_df'] == expected_hsd))


# in a script file
if __name__ == '__main__':
    unittest.main()
