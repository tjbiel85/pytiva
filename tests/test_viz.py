import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.viz import df_mean_rate_by_category, fig_lineplot_mean_rate_by_category

# local test config
import testconfig


class TestViz(unittest.TestCase):
    def setUp(self):
        self.ts_concurrency_test_data = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['TS_CONCURRENCY']),
            parse_dates=['timestamp'],
            index_col='timestamp'
        )
        self.ts_concurrency_test_data['dayofweek'] = self.ts_concurrency_test_data.index.map(lambda x: x.day_name())

    def test_lineplot_mean_rate_by_category(self):
        df_ref = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DF_MEAN_RATE_BY_CATEGORY']),
                             index_col=['dayofweek', 'timestamp_bin'])

        df_mean_rates = df_mean_rate_by_category(self.ts_concurrency_test_data,
                                                 metric_col='concurrent_activity_count',
                                                 category_col='dayofweek')

        self.assertTrue(all(df_ref == df_mean_rates))


    def test_lineplot_mean_rate_by_category_with_ci(self):
        df_ref = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DF_MEAN_RATE_BY_CATEGORY_WITH_CI']),
                             index_col=['dayofweek', 'timestamp_bin'])

        df_mean_rates = df_mean_rate_by_category(self.ts_concurrency_test_data,
                                                 metric_col='concurrent_activity_count',
                                                 category_col='dayofweek',
                                                 include_ci=0.95)

        self.assertTrue(all(df_ref == df_mean_rates))

    def test_lineplot_fig_mean_rate_by_category_returns_subplot(self):
        df_ref = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DF_MEAN_RATE_BY_CATEGORY_WITH_CI']),
                             index_col=['dayofweek', 'timestamp_bin'])

        ax = fig_lineplot_mean_rate_by_category(df_ref)

        # this is not great, but you can't import AxesSubplot because it's made in a factory
        self.assertTrue('matplotlib.axes._subplots.AxesSubplot' in str(type(ax)))


# in a script file
if __name__ == '__main__':
    unittest.main()
