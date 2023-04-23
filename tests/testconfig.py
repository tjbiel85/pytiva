import os
import pandas as pd

WD = r'test_data'

TESTDATA = {
    'DS_ACTIVITY': 'testdata-ds_activity.csv',
    'DS_CASES': 'testdata-ds_cases.csv',
    'DS_CASE_EVENTS': 'testdata-ds_case_events.csv',
    'DS_CASE_MEDS': 'testdata-ds_case_meds.csv',
    'STAFFING_LONG': 'testdata-staffing_long.csv',
    'TS_CONCURRENCY': 'testdata-ts_concurrency.csv',
    'ADS_FROM_MEDS': 'testdata-ads_from_meds.csv',
    'ADS_EVENTS_ONLY': 'testdata-ads_event_based_only.csv',
    'EVENT_BASED_ACTIVITY_DEFINITIONS': 'testdata-event_based_activity_definitions.json',
    'EXPECTED_STUDY_MEMBERS_AND_COUNTS': 'testdata-expected_study_members_and_counts.json',
    'DUPLICATED_GANTT': 'testdata-expected_duplicated_gantt.csv',
    'UNDUPLICATED_GANTT': 'testdata-expected_unduplicated_gantt.csv',
    'ONE_CASE_GANTT': 'testdata-expected_one_case_gantt.csv',
    'ONE_CASE_GANTT_PNG': 'comparison_gantt_one_case.png',
    #'ONE_CASE_GANTT_PNG_SAMPLE_SHA512_HEXDIGEST': '9e0c9a152bd912ce6b1bc6d0e0f1f1ed075d6e99dda4268d70a7496c380bd0dd89378f645f943ade972d1615152b7ccf1189d3b8953ac83290291e7c7b1e2144',
    'DS_STAFFING_ACTIVITY': 'testdata-ds_staffing_activity.csv',
    'DS_RESOURCES_LIMITED_BY_PS_DICT': 'testdata-ds_resources_limited_by_ps_dict.csv',
    'DS_RESOURCES_LIMITED_BY_DATE_LIST': 'testdata-ds_resources_limited_by_date_list.csv',
    'DS_RESOURCES_LIMITED_BY_DATE_LIST_AND_PS_DICT': 'testdata-ds_resources_limited_by_date_list_and_ps_dict.csv',
    'ADS_GENERATE_RESOURCE_ACTIVITY_W_PS_DICT': 'testdata-ads_generate_resource_activity_w_ps_dict.csv'
}

TESTDATA_CSV_DICT_FOR_DATASETS = {
    'ds_cases': {'FILEPATH': os.path.join(WD, TESTDATA['DS_CASES'])},
    'ds_case_meds': {'FILEPATH': os.path.join(WD, TESTDATA['DS_CASE_MEDS'])},
    'ds_case_events': {'FILEPATH': os.path.join(WD, TESTDATA['DS_CASE_EVENTS'])}
}

TESTDATA_STUDY_DATES = (pd.to_datetime('2021-10-01'), pd.to_datetime('2021-12-31'))

ACTIVITY_COLS_TO_VALID_CASES_COLS_MAP = {
    # a dictionary to allow activity testdata to be mapped to anesthesia cases
    'activity_start': 'anesthesia_start',
    'activity_end': 'anesthesia_end',
    'activity': 'procedure'
}

STAFF_SHIFT_DEFINITIONS =[
        {
            'label': 'd2f6c941bd6fbf44f16a63525afee4ad36ebca60494a',
            'start': pd.to_timedelta(7, unit='hour'),
            'duration': pd.to_timedelta(8, unit='hour'),
            'capacity': 0
        },

        {
            'label': 'aef57b58d44e427be333ee061c32c210453cdd807fd29c12525bd9d6809b',
            'start': pd.to_timedelta(7, unit='hour'),
            'duration': pd.to_timedelta(10, unit='hour'),
            'capacity': 0.5
        },

        {
            'label': 'd011c2c2bf3212b22588b138dab6f',
            'start': pd.to_timedelta(7, unit='hour'),
            'duration': pd.to_timedelta(24, unit='hour'),
            'capacity': 1
        },

        {
            'label': 'a11eadcfa7f7f1d7baaa5a71069b77e2868e441cc122f1076',
            'start': pd.to_timedelta(7, unit='hour'),
            'duration': pd.to_timedelta(12, unit='hour'),
            'capacity': 1
        },

        {
            'label': '4eef4f7220452e4441f87ada0c1adf2d575c7f0b1f06d2',
            'start': pd.to_timedelta(19, unit='hour'),
            'duration': pd.to_timedelta(12, unit='hour'),
            'capacity': 1
        },

        {
            'label': '13d52c88b42eb99fab11a388d0f4d5bd',
            'start': pd.to_timedelta(7, unit='hour'),
            'duration': pd.to_timedelta(8, unit='hour'),
            'capacity': 1
        },

        {
            'label': '63fcce7f13ec56a90ab5f572cf81fb7c32a1842c11accf',
            'start': pd.to_timedelta(6, unit='hour'),
            'duration': pd.to_timedelta(12, unit='hour'),
            'capacity': 1
        },

        {
            'label': 'd25ccc6afccce37b64f623656',
            'start': pd.to_timedelta(18, unit='hour'),
            'duration': pd.to_timedelta(12, unit='hour'),
            'capacity': 1
        }
    ]
