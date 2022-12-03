import unittest
import os
import pandas as pd

# local module to be tested
from pytiva.anesthesia import AnesthesiaCaseEventsDataSet
from pytiva.activity import ActivityDataSet

WD = r'test_data'
EVENT_TEST_DATA_FILENAME = 'event_test_data.csv'
NEURAXIAL_REFERENCE_FILENAME = 'neuraxial_labor_activity_dataset_test.csv'
NEURAXIAL_EVENT_PARAMS = {
    'start_event': '4132311845cdd970ff76ecc6dfdd51c32a124275b0f8e3552d287f5e95edfe124132311845cdd970ff76ecc6dfdd51c32a1',
    'end_event': '80da3163dee38ffaf6ee8dc8278cf3c7c0ba60bea0f7d3eeb90f0dc5b97da0e180da3163de',
    'activity_name': 'Neuraxial labor analgesia'
}

class TestAnesthesiaCaseEventsDataSet(unittest.TestCase):
    def setUp(self):
        self.df_ref = pd.read_csv(
            os.path.join(WD, EVENT_TEST_DATA_FILENAME),
            #parse_dates=['event_datetime']
        )

    def test_object_from_df(self):
        # the default activity test data set doesn't have columns appropriate for an anesthesia case data set
        ds = AnesthesiaCaseEventsDataSet(self.df_ref)
        self.assertIsInstance(ds, AnesthesiaCaseEventsDataSet)

    def test_ads_from_starts_and_ends(self):
        ds = AnesthesiaCaseEventsDataSet(self.df_ref)
        ads = ds.activity_ds_from_start_and_end_events(**NEURAXIAL_EVENT_PARAMS)
        ads_ref_df = pd.read_csv(os.path.join(WD, NEURAXIAL_REFERENCE_FILENAME))
        self.assertTrue(all(ads._df == ads_ref_df))


# in a script file
if __name__ == '__main__':
    unittest.main()
