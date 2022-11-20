import hashlib
import random
import pandas as pd


def hash_and_slash(x, slice_size=200):
    slice_offset = random.randint(0,55)
    slice_end = slice_offset + slice_size
    hashed = hashlib.sha256(str(x).encode('utf-8')).hexdigest()
    hashed = hashed + hashed
    return hashed[slice_offset:slice_size]


def hash_cols_in_df(df, hash_func, cols):
    """
    # hash these columns, obfuscating their contents
    # but do so in a fashion that makes the same hash for each input value
    :param df: DataFrame
    :param hash_func:
    :param cols:
    :return: a hashed version of the DataFrame
    """
    df_out = df.copy()

    for h in cols:
        if h in df_out.columns:
            h_unique_vals = [str(s) for s in df_out[h].unique()]
            h_hashmap = {v: hash_func(v) for v in h_unique_vals}

            df_out[h] = df_out[h].astype(str).map(h_hashmap)

    return df_out


def random_timedelta(unit_range=[-1000000, 1000000], unit='S'):
    return pd.to_timedelta(random.randint(*unit_range), unit)


def timedelta_offset_cols_in_df(df, td_func, cols):
    """Generate a (randomized) timedelta offset using td_func and apply it
    to the value(s) in cols.

    Intended to be called once per (row) entry for procedure records.
    """
    df_out = df.copy()
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
