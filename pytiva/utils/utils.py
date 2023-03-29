import hashlib
import os
import random
import pandas as pd


def hash_and_slash(x, slice_size=200):
    """
    Hash a value x and then trim it to contain slice_size characters.

    Bakes in a random offset for the start of the slice so they cannot be recreated.
    :param x:
    :param slice_size:
    :return:
    """
    hashed = hashlib.sha256(str(x).encode('utf-8')).hexdigest()

    salt_offset_start = random.randint(0,255)
    salt_end = salt_offset_start + random.randint(0,255)
    salt = (hashed + hashed)[salt_offset_start:salt_end]

    salted = salt+hashed

    rehashed = hashlib.sha256(str(salted).encode('utf-8')).hexdigest()

    slice_offset = random.randint(0, 55)
    slice_end = slice_offset + slice_size
    slashed = rehashed[slice_offset:slice_end]
    return slashed


def hash_cols_in_df(df, cols, hash_func=None):
    """
    # hash these columns, obfuscating their contents
    # but do so in a fashion that makes the same hash for each input value
    :param df: DataFrame
    :param hash_func:
    :param cols:
    :return: a hashed version of the DataFrame
    """
    df_out = df.copy()

    if hash_func is None:
        hash_func = hash_and_slash

    for h in cols:
        if h in df_out.columns:
            h_unique_vals = [str(s) for s in df_out[h].unique()]
            h_hashmap = {v: hash_func(v) for v in h_unique_vals}

            df_out[h] = df_out[h].astype(str).map(h_hashmap)

    return df_out


def random_timedelta(unit_range=[-1000000, 1000000], unit='S'):
    return pd.to_timedelta(random.randint(*unit_range), unit)


def timedelta_offset_cols_in_df(df, cols, td_func = None):
    """Generate a (randomized) timedelta offset using td_func and apply it
    to the value(s) in cols.

    Intended to be called once per (row) entry for procedure records.
    """
    df_out = df.copy()

    if td_func is None:
        td_func = random_timedelta

    for i, data in df_out.iterrows():
        offset = td_func()

        for c in cols:
            # apply the offset to each target column value
            df_out.loc[i, c] = df_out.loc[i, c] + offset

    return df_out


def datetime_to_activity_timespan(df, datetime_col, td_before, td_after,
                                  before_out='activity_start',
                                  after_out='activity_end',
                                  inplace=True):
    """
    Helper function to convert a single datetime time point to an activity time span
    i.e. to generate activity_start (before the datetime) and an activity_end (after
    the datetime).

    params:
    df is a pandas DataFrame object
    datetime_col is the column to be used as the single datetime time point
    td_before and td_after should be timedelta objects

    returns a DataFrame object with the additional columns, or a copy of the same
    if inplace is False

    """
    if not inplace:
        df = df.copy()

    df[before_out] = df[datetime_col].apply(lambda x: x - td_before)
    df[after_out] = df[datetime_col].apply(lambda x: x + td_after)

    return df


def dump_csv_from_excel(excel_filepath, wd_out, sheets,
                        csv_extension='csv', csv_prefix=None):
    """
    Helper function to get CSVs out of Excel sheets.

    Expects a config_dict that looks something like:

    excel_filepath: complete path to Excel file
    wd_out: working directory to dump CSV files
    sheets: collection with values like { 'SHEET_LABEL': 'Base', 'CSV_FILENAME': 'cases' }
    csv_extension: optional
    csv_prefix: prepended to csv_filenames
    """

    dumped = []

    for sheet_key, sheet_config in sheets.items():
        # read in
        xl = pd.read_excel(excel_filepath, sheet_config['SHEET_LABEL'])

        # where to?
        csv_filename = '.'.join([sheet_config['CSV_FILENAME'], csv_extension])
        if csv_prefix is not None:
            csv_filename = csv_prefix + csv_filename

        # dump out
        dump_filepath = os.path.join(wd_out, csv_filename)
        xl.to_csv(dump_filepath, index=False)
        dumped.append(dump_filepath)

    return dumped

