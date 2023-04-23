import unittest
import json
import os

# local module to be tested
from pytiva.anesthesia import datasets_from_csv_data, AnesthesiaStudy

# local test config
import testconfig

# read in the expected dataset members under certain circumstances, including limiting by dates or a list of procedures
h = open(os.path.join(testconfig.WD, testconfig.TESTDATA['EXPECTED_STUDY_MEMBERS_AND_COUNTS']), "r")
EXPECTED_DS = json.load(h)
h.close()


class TestAnesthesiaStudy(unittest.TestCase):
    def test_study_from_csv_dict(self):
        comp = EXPECTED_DS['BASE']
        datasets = datasets_from_csv_data(testconfig.TESTDATA_CSV_DICT_FOR_DATASETS)
        study = AnesthesiaStudy(**datasets)
        self.assertTrue(study._member_ds_and_counts == comp['MEMBERS'])

    def test_filter_by_anesstart(self):
        comp = EXPECTED_DS['LIMITED_BY_DATES']
        datasets = datasets_from_csv_data(testconfig.TESTDATA_CSV_DICT_FOR_DATASETS)
        study = AnesthesiaStudy(**datasets)
        study.limit_by_dates(*comp['DATES'])
        self.assertTrue(study._member_ds_and_counts == comp['MEMBERS'])

    def test_filter_by_lst_procedure(self):
        comp = EXPECTED_DS['LIMITED_BY_LIST']
        datasets = datasets_from_csv_data(testconfig.TESTDATA_CSV_DICT_FOR_DATASETS)
        study = AnesthesiaStudy(**datasets)
        study.limit_by_list(comp['TARGET_COL'], comp['VALUES'])
        self.assertTrue(study._member_ds_and_counts == comp['MEMBERS'])

    def test_study_config(self):
        comp = EXPECTED_DS['BY_STUDY_CONFIG']
        datasets = datasets_from_csv_data(testconfig.TESTDATA_CSV_DICT_FOR_DATASETS)
        study = AnesthesiaStudy(**datasets)
        study.process_study_config(comp['CONFIG'])
        self.assertTrue(study._member_ds_and_counts == comp['MEMBERS'])


# in a script file
if __name__ == '__main__':
    unittest.main()
