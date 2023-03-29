from .AnesthesiaDataSet import AnesthesiaDataSet
from ..activity import ActivityDataSet


class AnesthesiaCaseEventsDataSet(AnesthesiaDataSet):
    """
    expected columns:
        * a required admission or encounter ID
        * an optional patient ID
        * event datetime
        * event name or label
        * optional event note text

    save off a typical map for those columns elsewhere in a data cleaning util?
    """

    _required_columns = [
        'case_id',
        'event_label',
        'event_datetime'
    ]

    _case_id_col = 'case_id'
    _event_col = 'event_label'
    _datetime_col = 'event_datetime'

    # for enforcement as datetime objects during init
    _datetime_columns = [
        _datetime_col
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def activity_ds_from_start_and_end_events(self, start_event, end_event, activity_label='activity'):
        """
        Find paired instances of events start_event and end_event in DataFrame df, and use
        these to generate an ActivityDataSet.

        # TODO: more advanced logic for things that have to happen during activity, i.e.
        # things that have to happen in between events?
        """
        df = self._df

        targets = df[df[self._event_col].isin([start_event, end_event])][
            [self._datetime_col, self._event_col, self._case_id_col]].sort_values(self._datetime_col)
        targets['next'] = targets[self._event_col].shift(-1)
        targets['activity_end'] = targets[self._datetime_col].shift(-1)
        targets['paired'] = targets.apply(lambda x: x[self._event_col] == start_event and x['next'] == end_event, axis=1)
        activity = targets[targets['paired']][[self._datetime_col, self._case_id_col, 'activity_end']]
        activity.rename(columns={'event_datetime': 'activity_start'}, inplace=True)
        activity['activity'] = activity_label

        return ActivityDataSet(activity.reset_index(drop=True))
