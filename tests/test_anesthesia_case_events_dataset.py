import unittest
import json
import os
import pandas as pd

# local module to be tested
from pytiva.anesthesia import AnesthesiaCaseEventsDataSet
from pytiva.activity import ActivityDataSet

# local test config
import testconfig


class TestAnesthesiaCaseEventsDataSet(unittest.TestCase):
    def setUp(self):
        self.df_ref = pd.read_csv(
            os.path.join(testconfig.WD, testconfig.TESTDATA['DS_CASE_EVENTS']),
            #parse_dates=['event_datetime']
        )

    def test_object_from_df(self):
        # the default activity test data set doesn't have columns appropriate for an anesthesia case data set
        ds = AnesthesiaCaseEventsDataSet(self.df_ref)
        self.assertIsInstance(ds, AnesthesiaCaseEventsDataSet)

    def test_ads_from_starts_and_ends(self):
        ds = AnesthesiaCaseEventsDataSet(self.df_ref)
        h = open(os.path.join(testconfig.WD, testconfig.TESTDATA['EVENT_BASED_ACTIVITY_DEFINITIONS']), "r")
        definitions = json.load(h)
        h.close()

        activity_df = pd.concat([ds.activity_ds_from_start_and_end_events(**d) for d in definitions], ignore_index=True)
        ads_ref_df = ActivityDataSet(pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['ADS_EVENTS_ONLY'])))._df
        self.assertTrue(all(activity_df == ads_ref_df))


# in a script file
if __name__ == '__main__':
    unittest.main()
