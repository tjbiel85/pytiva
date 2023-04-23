import pandas as pd

from .ProviderShift import ProviderShift


def provider_shift_defs_to_kv_dict(definitions, exclude_zero_capacity=False):
    return {
        d['label']: ProviderShift(**d)
        for d in definitions
        if not (exclude_zero_capacity and d['capacity'] == 0)
    }


def matching_shift_from_collection(label, collection):
    """Return matching ProviderShift object in collection, according to label"""
    label = str(label).upper()
    match = False
    for s in collection:
        comparator = str(s.label).upper()
        if comparator == label:
            if not match:
                match = s
            else:
                raise Exception(f'Found more than one match ({s} and {match})')
    return match


def matching_ps_from_dictionary(key, dictionary):
    """
    Return matching ProviderShift object in dictionary, according to key. Assumes dictionary is structured as
    {key: ProviderShift object}

    Is also case-sensitive--might need to process incoming schedule data in case of irregularities.
    """
    match = key in dictionary.keys()
    if match:
        return dictionary[key]
    else:
        raise Exception(f'Could not find matching key in dictionary ({key})')
    pass


def earliest_starting_time(shift_collection):
    """Find the ProviderShift object in shift_collection with the earliest starting time"""
    earliest = False
    for i in range(len(shift_collection)):
        if i == 0:
            earliest = shift_collection[i].start
        else:
            comparison = shift_collection[i].start
            if comparison < earliest:
                earliest = comparison

    return earliest


def latest_ending_time(shift_collection):
    """Find the ProviderShift object in shift_collection with the latest ending time"""
    latest = False
    for i in range(len(shift_collection)):
        if i == 0:
            latest = shift_collection[i].end
        else:
            comparison = shift_collection[i].end
            if comparison > latest:
                latest = comparison

    return latest


def qgenda_task_grid_to_long_format(filepath, skiprows=3,
                                    assignment_label='assignment',
                                    dates_label='date',
                                    staff_label='staff',
                                    months_format='%b-%y'):
    """
    Processes a Qgenda staffing export in "grid by task" format from an Excel file at filepath.

    Returns a pandas DataFrame in "long" format, where each row is a single staff assignment
    with a numeric automatic index and columns ['assignment', 'date', 'staff'] e.g.:

                          assignment       date        staff
            0      Fel-ICU-Incentive 2021-10-02  Montejano J
            1      Fel-ICU-Incentive 2021-10-10  Montejano J
            2                Surge 2 2021-11-17   Hennigan A
            3                Surge 2 2021-11-18   Hennigan A
            4                Surge 2 2021-11-19      Douin D
            etc.

    :param filepath: path to Excel file
    :param skiprows: by default, first 3 rows are cruft
    :param assignment_label: what are the assignments labeled as in the file?
    :param dates_label: what label should be applied to the date column?
    :param staff_label: what are the staff entries labeled as in the file?
    :param months_format: what format are the months exported as in the file?
    :return: a pandas DataFrame in "long" format
    """
    # import unprocessed Excel file from Qgenda export
    # skip the first 3 rows--these are cruft
    df = pd.read_excel(filepath, skiprows=skiprows)

    # fill assignments "downward" in first column
    df[df.columns[0]] = df[df.columns[0]].ffill()

    # fill month component "left to right" across first row
    df[:1] = df[:1].ffill(axis=1, )

    # 1) slice just the data (who is assigned to these things on each date, and trim the date entries themselves)
    # 2) slice away the assignments, move them into a DataFrame index, and relabel the index as such
    data_row_start = 3
    column_label_start = 1
    column_assignments = 0
    data_columns = df.columns[column_label_start:]
    assignment_labels = df.iloc[:, 0][data_row_start:]
    data_df = df[data_row_start:][data_columns]
    data_df[assignment_label] = assignment_labels
    data_df.set_index(assignment_label, inplace=True)

    # reconstruct the dates for the assignments
    months = df.iloc[0][column_label_start:]
    days = df.iloc[1][column_label_start:]
    dates = [pd.to_datetime(str(m), format=months_format) + pd.to_timedelta(d - 1, unit='day') for m, d in
             zip(months, days)]

    # use this as the column labels for the data
    data_df.columns = dates
    data_df.columns.name = dates_label

    # wide to long
    data_long = pd.DataFrame(data_df.stack()).reset_index()
    data_long[staff_label] = data_long[0]
    data_long.drop(0, axis=1, inplace=True)

    return data_long
