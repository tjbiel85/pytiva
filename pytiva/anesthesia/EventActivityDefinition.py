from ..activity import ActivityDataSet


class EventActivityDefinition(object):
    def __init__(self, start_event, end_event, case_sensitive=False,
                 activity_label='activity', offset_start=None, offset_end=None,
                 max_duration_quantile=1, max_duration_factor=1):
        """

        :param start_event:
        :param end_event:
        :param case_sensitive:
        :param activity_label:
        :param offset_start: optional pandas TimeDelta
        :param offset_end: optional pandas TimeDelta
        """
        self.start_event = start_event
        self.end_event = end_event
        self.case_sensitive = case_sensitive
        self.activity_label = activity_label
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.max_duration_quantile = max_duration_quantile
        self.max_duration_factor = max_duration_factor
        pass

    def apply_to_ds(self, ds):
        """
        Expects a DataSet, particularly an AnesthesiaCaseEventsDataSet, as ds.
        :param ds: AnesthesiaCaseEventsDataSet
        :return:
        """
        df = ds._df
        activity_label = self.activity_label
        start_event = self.start_event
        end_event = self.end_event

        if self.case_sensitive == False:
            start_event = start_event.lower()
            end_event = end_event.lower()
            df[ds._event_col] = df[ds._event_col].apply(str.lower)

        targets = df[df[ds._event_col].isin([start_event, end_event])][
            [ds._datetime_col, ds._event_col, ds._case_id_col]].sort_values(ds._datetime_col)

        targets['next'] = targets[ds._event_col].shift(-1)
        targets['activity_end'] = targets[ds._datetime_col].shift(-1)
        targets['paired'] = targets.apply(lambda x: x[ds._event_col] == start_event and
                                                    x['next'] == end_event,
                                          axis=1)

        activity = targets[targets['paired']][[ds._datetime_col, ds._case_id_col, 'activity_end']]
        activity.rename(columns={'event_datetime': 'activity_start'}, inplace=True)
        activity['activity'] = activity_label

        ds_activity = ActivityDataSet(activity.reset_index(drop=True))

        if self.offset_start is not None:
            ds_activity.apply_offset(self.offset_start)

        if self.offset_end is not None:
            ds_activity.apply_offset(self.offset_end, apply_to_start=False)

        if self.max_duration_quantile != 1 or self.max_duration_factor != 1:
            # truncate with a maximum duration
            maximum_duration = ds_activity['duration'].quantile(self.max_duration_quantile) * self.max_duration_factor
            ds_activity.enforce_maximum_duration(maximum_duration)

        return ds_activity
