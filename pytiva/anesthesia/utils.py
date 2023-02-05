import pandas as pd
from . import AnesthesiaCaseDataSet, AnesthesiaCaseMedicationsDataSet, AnesthesiaCaseEventsDataSet, AnesthesiaCaseStaffingDataSet


def datasets_from_csv_data(
        csv_dict,  # filepath, category of data, column map
        # maybe limit on dates and procedures and locations, and extract activity from events in a subsequent step?
):
    """

    Processes csv files and creates an AnesthesiaStudy object.

    Returns an AnesthesiaStudy object loaded up with available DataSet objects.

    """
    _dataset_options = {
        'ds_cases': AnesthesiaCaseDataSet,
        'ds_case_meds': AnesthesiaCaseMedicationsDataSet,
        'ds_case_events': AnesthesiaCaseEventsDataSet,
        'ds_case_staffing': AnesthesiaCaseStaffingDataSet
    }
    _filepath_label = 'FILEPATH'
    _column_map_label = 'COLUMN_MAP'
    _column_limit_label = 'LIMIT_COLUMNS_BY_MAP'

    datasets = {}

    for ds, ds_config in csv_dict.items():
        if ds in _dataset_options.keys():
            df = pd.read_csv(ds_config[_filepath_label])

            # rename columns?
            if _column_map_label in ds_config.keys():
                colmap = ds_config[_column_map_label]
                df.rename(columns=colmap, inplace=True)

            # slim to only columns in the column map?
            if _column_limit_label in ds_config.keys() and ds_config[_column_limit_label] == True:
                df = df[colmap.values()]

            # set aside a DataSet of the specified sub-type
            datasets[ds] = _dataset_options[ds](df)

    return datasets
