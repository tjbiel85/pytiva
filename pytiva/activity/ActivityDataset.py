import operator
import pandas as pd
import numpy as np
from tqdm import tqdm


class ActivityDataset(object):
    """Empty docstring"""

    required_columns = ['activity_start', 'activity_end', 'activity']
    timeseries_index_label = 'timestamp'

    def __init__(
            self,
            data,
            column_map={
                'activity_start': 'activity_start',
                'activity_end': 'activity_end',
                'activity': 'activity'
            },
            default_resolution='1Min'
    ):
        self._default_resolution = default_resolution
        self._data = data
        self.df = pd.DataFrame(data)

        # if the expected columns are already present, this does nothing
        self.df.rename(columns=column_map, inplace=True)

        for dtc in ['activity_start', 'activity_end']:
            self.df[dtc] = pd.to_datetime(self.df[dtc])

        self.df['activity_start'] = self.df['activity_start'].apply(lambda x: x.floor(self._default_resolution))
        self.df['activity_end'] = self.df['activity_end'].apply(lambda x: x.ceil(self._default_resolution))

        # TODO: check to see if all required_columns are present

    def value_between_row_values(
            row,
            value,
            column_left='activity_start',
            column_right='activity_end',
            include_left=True,
            include_right=False
    ):

        if include_left == True:
            l_func = operator.ge
        else:
            l_func = operator.gt

        if include_right == True:
            r_func = operator.le
        else:
            r_func = operator.lt

        if l_func(value, row[column_left]) and r_func(value, row[column_right]):
            return True
        else:
            return False

    def datetime_to_dow_based_timedelta(x):
        """
        Sets aside adds 24 hours
        """
        dow_part = pd.to_timedelta(x.dayofweek * 24, unit='H')
        hours_part = pd.to_timedelta(x.hour, unit='H')
        minutes_part = pd.to_timedelta(x.minute, unit='Min')
        seconds_part = pd.to_timedelta(x.second, unit='sec')

        return dow_part + hours_part + minutes_part + seconds_part

    def _date_range_from_start_and_end_points(self, drop_duplicates=True, dropna=True):
        starts = self.df['activity_start'].values
        ends = self.df['activity_end'].values
        both = np.concatenate([starts, ends])
        date_range = pd.Series(both)

        if drop_duplicates:
            date_range.drop_duplicates(inplace=True)

        if dropna:
            date_range.dropna(inplace=True)

        return date_range

    def _collect_concurrency(
            self,
            date_range=None,
            column_left='activity_start',
            column_right='activity_end',
            func=value_between_row_values,
            limit=None
    ):
        # TODO: multithread this, perhaps separate out a generator from the rest to hand off
        # and then re-aggregate

        concurrency_collection = []

        if date_range is None:
            # by default, construct a date range from the discrete points
            # within the activity start and end data
            date_range = self._date_range_from_start_and_end_points()

        if limit is None:
            limit = len(date_range)

        for d in tqdm(date_range[:limit]):
            df_filter = self.df.apply(
                lambda x: func(
                    x,
                    d,
                    column_left,
                    column_right
                ),
                axis=1
            )
            concurrency_collection.append({
                self.timeseries_index_label: d,
                'concurrent_activity_count': len(self.df[df_filter])
            })

        return concurrency_collection

    def concurrency_ts(self, resolution=None):
        # by default, use the... self.default_resolution
        cc = pd.DataFrame(self._collect_concurrency()).set_index(self.timeseries_index_label)

        if resolution is None:
            resolution = self._default_resolution

        reindexed = cc.reindex(pd.date_range(start=cc.index.min(), end=cc.index.max(), freq=resolution))
        reindexed.index.name = self.timeseries_index_label
        return reindexed.fillna(method='ffill')
