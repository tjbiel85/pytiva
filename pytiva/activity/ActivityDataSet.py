import itertools
import multiprocessing
import os

import numpy as np
import pandas as pd
from tqdm import tqdm

from .utils import value_between_row_values, check_start_of_concurrent_activity, check_end_of_concurrent_activity
from ..viz import activity_data_to_gantt_data, gantt_plot

from ..dataset import DataSet


class ActivityDataSet(DataSet):
    """
    Subclassed from pytiva.dataset.DataSet

    meant to hold info about activities performed, which should generally be some phenomenon bound by two timepoints

    Always has an activity_start and activity_end column, both of which are datetimes, so each row is a span of time.

    Has methods to determine concurrency (i.e. overlapping activities).
    """

    _activity_start_col = 'activity_start'
    _activity_end_col = 'activity_end'
    _duration_col = 'duration'
    _required_columns = [_activity_start_col, _activity_end_col]
    _datetime_columns = [_activity_start_col, _activity_end_col]
    _concurrency_ts_start_col = 'is_start'
    _concurrency_ts_end_col = 'is_end'
    _ts_index_label = 'timestamp'

    _forbidden_columns = []#['duration']

    def __init__(
            self,
            data,
            default_resolution='1Min',
            reset_index_on_init=True,
            generate_duration_on_init=True,
            *args, **kwargs
    ):
        self._default_resolution = default_resolution

        super_init_return_val = super().__init__(data=data, *args, **kwargs)

        self._df[self._activity_start_col] = self._df[self._activity_start_col].apply(
            lambda x: x.floor(self._default_resolution)
        )
        self._df[self._activity_end_col] = self._df[self._activity_end_col].apply(
            lambda x: x.ceil(self._default_resolution)
        )

        if generate_duration_on_init:
            self.generate_duration()

        if reset_index_on_init:
            self._df.reset_index(inplace=True, drop=True)

        self._resort_columns()

    def generate_duration(self):
        self._df[self._duration_col] = self._df[self._activity_end_col] - self._df[self._activity_start_col]
        pass

    def apply_offset(self, td_offset, apply_to_start=True, regenerate_duration=True):
        if apply_to_start:
            self._df[self._activity_start_col] = self._df[self._activity_start_col] + td_offset
        else:
            self._df[self._activity_end_col] = self._df[self._activity_end_col] + td_offset

        if regenerate_duration:
            self.generate_duration()

        pass

    def enforce_maximum_duration(self, maximum_duration, regenerate_duration=True):
        self._df.loc[self._df['duration'] > maximum_duration, 'activity_end'] = self._df['activity_start'].apply(lambda x: x + maximum_duration)

        if regenerate_duration:
            self.generate_duration()

        pass

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
        starts = self._df[self._activity_start_col].values
        ends = self._df[self._activity_end_col].values
        both = np.concatenate([starts, ends])
        date_range = pd.Series(both)

        if drop_duplicates:
            date_range.drop_duplicates(inplace=True)

        if dropna:
            date_range.dropna(inplace=True)

        return date_range

    # TODO: functools.partial
    def _mp_concurrency_helper(self, args):
        data_df, datetime, column_left, column_right, func, ts_index_label = args

        # filter to the concurrent records of interest
        df_filter = data_df.apply(
            lambda x: func(
                x,
                datetime,
                column_left,
                column_right
            ),
            axis=1
        )
        return {
            ts_index_label: datetime,
            'concurrent_activity_count': len(data_df.loc[df_filter])
        }

    def _collect_concurrency(
            self,
            date_range = None,
            column_left = _activity_start_col,
            column_right = _activity_end_col,
            func = value_between_row_values,
            limit = None,
            mp = True
    ):
        """
        :param date_range:
        :param column_left:
        :param column_right:
        :param func:
        :param limit:
        :param mp:
        :return:
        """
        concurrency_collection = []

        if date_range is None:
            # by default, construct a date range from the discrete points
            # within the activity start and end data
            date_range = self._date_range_from_start_and_end_points()

        if limit is None:
            limit = len(date_range)

        if mp:
            # iterable for data_df, datetime, column_left, column_right, func , ts_index_label
            # note to self: do not pass self
            concurrency_iterator = [(self._df, datetime, column_left, column_right, func, self._ts_index_label)
                                    for datetime in date_range[:limit]]

            with multiprocessing.Pool(processes=os.cpu_count()-1) as pool:
                concurrency_collection = pool.map(self._mp_concurrency_helper, concurrency_iterator)
        else:
            for d in tqdm(date_range[:limit]):
                # TODO: multithread this, perhaps separate out a generator from the rest to hand off
                df_filter = self._df.apply(
                    lambda x: func(
                        x,
                        d,
                        column_left,
                        column_right
                    ),
                    axis=1
                )
                concurrency_collection.append({
                    self._ts_index_label: d,
                    'concurrent_activity_count': len(self._df[df_filter])
                })

        return concurrency_collection

    def concurrency_ts(self, resolution=None, *args, **kwargs):
        """

        :param resolution:
        :param args:
        :param kwargs:
        :return:
        """
        # by default, use the... self.default_resolution
        cc = pd.DataFrame(self._collect_concurrency(*args, **kwargs)).set_index(self._ts_index_label)

        if resolution is None:
            resolution = self._default_resolution

        reindexed = cc.reindex(pd.date_range(start=cc.index.min(), end=cc.index.max(), freq=resolution))
        reindexed.index.name = self._ts_index_label
        return reindexed.fillna(method='ffill')

    def _generate_stratified_df_slices(self, strata_cols, strip_forbidden_cols=True):
        """
        Generate slices of data in self using unique combinations of values in columns named by strata_cols.

        """
        combinations = [{
            strata_cols[i]: x[i] for i in range(len(x))
        } for x in itertools.product(*[self._df[c].unique() for c in strata_cols])]

        for c in combinations:
            df_slice = self._df
            for k, v in c.items():
                df_slice = df_slice[df_slice[k] == v]

                if strip_forbidden_cols:
                    df_slice = df_slice[ [c for c in df_slice.columns if c not in self._forbidden_columns] ]

                yield df_slice

    def fetch_unduplicated_concurrency(self, activities=None, activity_out_label='activity',
                                       strata=None):
        """
        Make use of _unduplicated_concurrency_to_df(), using it to generate unduplicated concurrency
        for an arbitrary collection of activities (e.g., medication, procedure, etc.), sliced according to strata.

        Strata, if provided, should be a collection of column labels. These will be used with
        activity.utils.col_val_combinations_to_dicts() to generate a slice of unique values for the provided columns
        and perform unduplication at that level.

        For example, the unduplication of concurrency could be performed at the level of case_id, or med_label and
        provider, or something else.

        :param activities:
        :param activity_out_label:
        :param strata:
        :return: a concatenated DataFrame of the unduplicated activity data
        """
        target = self

        if activities is not None:
            target = target[target.activity.isin(activities)]

        if strata is None:
            # no strata to group this stuff by
            df_out = self._unduplicated_concurrency_to_df(target)

        else:
            # stratify the unduplication
            # (great candidate for parallelization)
            slices = []
            for df_slice in self._generate_stratified_df_slices(strata):
                if len(df_slice) > 0:
                    slices.append(self._unduplicated_concurrency_to_df(ActivityDataSet(df_slice)))

            df_out = pd.concat(slices, ignore_index=True)

        df_out['activity'] = activity_out_label

        return type(self)(df_out)

    def _unduplicated_concurrency_to_df(self, ads):
        """
        Generate concurrency time series for provided ActivityDataSet ads, then unduplicate that activity.

        I.e., for two overlapping activity time spans, use the start time from the earlier one and the end time
        from the later one. And do this for all entries in the provided ActivityDataSet.
        """

        ts = ads.concurrency_ts()
        ts['prev'] = ts['concurrent_activity_count'].shift().fillna(0)

        ts[self._concurrency_ts_start_col] = ts.apply(func=check_start_of_concurrent_activity, axis=1)
        ts[self._concurrency_ts_end_col] = ts.apply(func=check_end_of_concurrent_activity, axis=1)

        paired_df = pd.DataFrame(
            [z for z in zip(ts[ts[self._concurrency_ts_start_col]].index, ts[ts[self._concurrency_ts_end_col]].index)],
            columns=[self._activity_start_col, self._activity_end_col]
        )

        return paired_df

    def hr_activity_summary(self, display_limit=3):
        """
        Returns a single string with the labels and counts for up to display_limit number
        of unique activity label entries. Looks something like:

            '"medication" (36118 entries), "regional procedure" (1531 entries), and 1 other'

        :param display_limit:
        :return:
        """

        activity_vc = self['activity'].value_counts()
        l_vc = len(activity_vc)
        omitted_count = l_vc - display_limit
        activity_vc_lst = []
        for label, number in activity_vc[:display_limit].iteritems():
            activity_vc_lst.append(f'"{label}" ({number} entries)')

        hr = ", ".join(activity_vc_lst)
        if omitted_count > 0:
            hr = hr + f', and {omitted_count} other'
            if omitted_count > 1:
                hr = hr + 's'

        return hr
