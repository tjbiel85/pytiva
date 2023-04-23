import unittest
import hashlib
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# local module to be tested
from pytiva.anesthesia import datasets_from_csv_data, AnesthesiaStudy, EventActivityDefinition
from pytiva.activity import ActivityDataSet
from pytiva.viz import activity_data_to_gantt_data, gantt_plot

# local test config
import testconfig

# read in the expected dataset members under certain circumstances, including limiting by dates or a list of procedures
h = open(os.path.join(testconfig.WD, testconfig.TESTDATA['EXPECTED_STUDY_MEMBERS_AND_COUNTS']), "r")
EXPECTED_DS = json.load(h)
h.close()


class TestGantt(unittest.TestCase):
    def setUp(self):
        datasets = datasets_from_csv_data(testconfig.TESTDATA_CSV_DICT_FOR_DATASETS)
        study = AnesthesiaStudy(**datasets)

        # activities
        h = open(os.path.join(testconfig.WD, testconfig.TESTDATA['EVENT_BASED_ACTIVITY_DEFINITIONS']),
                 "r")
        ea_definitions = json.load(h)
        h.close()

        study.ds_activity = ActivityDataSet(
            pd.concat([
                          EventActivityDefinition(**d).apply_to_ds(study.ds_case_events)
                          for d in ea_definitions
                      ] + [study.ds_case_meds.to_activity_dataset(pd.to_timedelta(2, unit='T'),
                                                                  pd.to_timedelta(3, unit='T'))._df]
                      ).reset_index(drop=True)
        )
        study.limit_by_dates(dt_start=testconfig.TESTDATA_STUDY_DATES[0], dt_end=testconfig.TESTDATA_STUDY_DATES[1])
        self.study = study

    def test_duplicated_gantt(self):
        comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['DUPLICATED_GANTT']))
        duplicated_gantt_df = activity_data_to_gantt_data(
            self.study.ds_activity, strata=['case_id', 'activity'], include_label_in_stratification=True
        )
        self.assertTrue(all(comp == duplicated_gantt_df))

    # def test_unduplicated_gantt(self):
    #    comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['UNDUPLICATED_GANTT']))
    #    unduplicated_gantt_df = activity_data_to_gantt_data(self.study.unduplicate_activity())
    #    self.assertTrue(all(comp == unduplicated_gantt_df))

    def test_one_case_gantt(self):
        comp = pd.read_csv(os.path.join(testconfig.WD, testconfig.TESTDATA['ONE_CASE_GANTT']))
        self.study.limit_by_list('case_id', ['355c8af6bc950d2dd9'])
        gantt_one_case_df = activity_data_to_gantt_data(self.study.ds_activity)
        self.assertTrue(all(comp == gantt_one_case_df))

    def test_gantt_png(self):
        gantt_png_filepath = os.path.join(testconfig.WD, testconfig.TESTDATA['ONE_CASE_GANTT_PNG'])
        with open(gantt_png_filepath, mode='rb') as f:
            comp_byte_sample = f.read(2 ** 10 * 8)

        comp_digest = hashlib.sha512(comp_byte_sample).hexdigest()

        self.study.limit_by_list('case_id', ['355c8af6bc950d2dd9'])
        gantt_one_case_df = activity_data_to_gantt_data(self.study.ds_activity)
        graph = gantt_plot(gantt_one_case_df)
        temp_png = 'GANTT_TEMP.png'
        plt.savefig(temp_png)

        with open(temp_png, mode='rb') as f:
            generated_byte_sample = f.read(2 ** 10 * 8)

        generated_digest = hashlib.sha512(generated_byte_sample).hexdigest()

        os.remove(temp_png)
        self.assertEqual(comp_digest, generated_digest)


# in a script file
if __name__ == '__main__':
    unittest.main()
