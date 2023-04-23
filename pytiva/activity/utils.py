import itertools
import operator
ORDERED_WEEKLY_DAY_NAME = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def value_between_row_values(
        row,
        value,
        column_left='activity_start',
        column_right='activity_end',
        include_left=True,
        include_right=False
):
    if include_left:
        l_func = operator.ge
    else:
        l_func = operator.gt

    if include_right:
        r_func = operator.le
    else:
        r_func = operator.lt

    if l_func(value, row[column_left]) and r_func(value, row[column_right]):
        return True
    else:
        return False


def minute_of_day(timestamp):
    return timestamp.hour * 60 + timestamp.minute


def concurrent_weekly_activity(df_cc, label='concurrent_activity_count'):
    """
    Expects pandas.DataFrame with DatetimeIndex
    :param df_cc:
    :return:
    """
    df_copy = df_cc.copy()
    df_copy['dayofweek'] = df_copy.index.dayofweek
    df_copy['day_name'] = df_copy.index.day_name()
    df_copy['minute_of_day'] = df_copy.index.map(minute_of_day)
    grouped = df_copy.groupby(['minute_of_day', 'day_name'])[label].mean()
    return grouped.unstack()[ORDERED_WEEKLY_DAY_NAME]


def check_end_of_concurrent_activity(row,
                                     activity_label='concurrent_activity_count',
                                     prev_label='prev'):
    if row[activity_label] == 0 and row[prev_label] > 0:
        return True
    else:
        return False


def check_start_of_concurrent_activity(row,
                                       activity_label='concurrent_activity_count',
                                       prev_label='prev'):
    if row[activity_label] > 0 and row[prev_label] <= 0:
        return True
    else:
        return False
