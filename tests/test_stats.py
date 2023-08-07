import unittest
import os
import pandas as pd

from pytiva.dataset import DataSet

# local test config
import testconfig


class TestStats(unittest.TestCase):
    def setUp(self):
        self.df_ref = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['DS_ACTIVITY']),
            parse_dates=['activity_start', 'activity_end']
        )

    def test_statistical_testing_of_group_means_anova(self):
        """
        unit test for expected results of ANOVA on test data using DataSet.test_group_means(), itself a wrapper for
        pytiva.stats.test_group_means()
        """
        self.df_ref['duration'] = (self.df_ref['activity_end'] - self.df_ref['activity_start']).dt.total_seconds()
        ds = DataSet(self.df_ref)
        tgm_result = ds.test_group_means('activity', 'duration')
        self.assertTrue(tgm_result[0] == testconfig.TESTDATA['EXPECTED_ANOVA_DICT'])

    def test_statistical_testing_of_group_means_hsd(self):
        """
        unit test for expected results of Tukey HSD on test data using DataSet.test_group_means(), itself a wrapper for
        pytiva.stats.test_group_means()
        """
        self.df_ref['duration'] = (self.df_ref['activity_end'] - self.df_ref['activity_start']).dt.total_seconds()
        ds = DataSet(self.df_ref)
        tgm_result = ds.test_group_means('activity', 'duration')
        expected_hsd = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['EXPECTED_TUKEY_HSD_DF']))
        self.assertTrue(all(tgm_result[1]['result_df'] == expected_hsd))


# in a script file
if __name__ == '__main__':
    unittest.main()
