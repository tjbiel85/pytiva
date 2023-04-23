import operator

import pandas as pd

from .DataSet import DataSet


class TimeSeriesDataSet(DataSet):
    """
    A parent class for time series data, generally representing a rectangular data object whose index is a sequential
    DateTimeIndex of some kind. Expects data structured in two columns: index and value.

    May optionally have metadata for each time point as well, and these can be required in child classes.
    """

    def __init__(self, data, start_dt=None, end_dt=None, fillna=0, freq='T', *args, **kwargs):
        if start_dt is None:
            start_dt = data.index.min()

        if end_dt is None:
            end_dt = data.index.max()

        if freq is None:
            freq = data.index.freq

        i = pd.date_range(start=start_dt, end=end_dt, freq=freq)

        super().__init__(data, *args, **kwargs)
        self._df = self._df.reindex(i).fillna(fillna)
        self._df.index.rename('ts_index', inplace=True)
