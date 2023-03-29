from ..dataset import DataSet

from ..utils import datetime_to_activity_timespan


class AnesthesiaDataSet(DataSet):
    """
    A parent class for various anesthesia-related DataSet objects to inherit from.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _with_timespans(self,
                        datetime_col,
                        td_offset_before,
                        td_offset_after):
        """
        Return a version of this DataSet with start and stop times, based on admin time plus supplied offsets.
        :param offset_before:
        :param offset_after:
        :return:
        """

        return datetime_to_activity_timespan(
            self,
            datetime_col=datetime_col,
            td_before=td_offset_before,
            td_after=td_offset_after,
            inplace=False
        )

    def limit_by_list(self, col, lst_items):
        """
        :param col: a label corresponding to a column in the DataFrame at self._df
        :param lst_items: allowable items; will be used in DataFrame[col].isin()
        :return: excluded items, in an object of the same type as self
        """
        mask = self._df[col].isin(lst_items)
        excluded = self._df.loc[ ~mask ]
        self._df = self._df.loc[ mask ]
        return type(self)(excluded)
