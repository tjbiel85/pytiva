from pandas import to_timedelta

from .AnesthesiaDataSet import AnesthesiaDataSet
from ..activity import ActivityDataSet


class AnesthesiaCaseMedicationsDataSet(AnesthesiaDataSet):
    """
    expected columns:
        * a required admission or encounter ID
        * an optional patient ID
        * event datetime
        * event name or label
        * optional event note text

    save off a typical map for those columns elsewhere in a data cleaning util?
    """
    _required_columns = ['case_id', 'med_datetime', 'med_label']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_activity_dataset(self,
                            offset_before,
                            offset_after,
                            activity_label='medication'):

        data = self._with_timespans(
            datetime_col='med_datetime',
            td_offset_before=offset_before,
            td_offset_after=offset_after
        )
        data['activity'] = activity_label
        return ActivityDataSet(data)
