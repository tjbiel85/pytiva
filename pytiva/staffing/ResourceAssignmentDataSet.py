from ..activity import ActivityDataSet
from .StaffingDataSet import StaffingDataSet
from ..dataset.TimeSeriesDataSet import TimeSeriesDataSet
from . import utils

import pandas as pd


class ResourceAssignmentDataSet(StaffingDataSet):
    """
    Representation of assigned (scheduled) resources.
    """
    _col_assignment_label = 'assignment'

    _required_columns = [
        _col_assignment_label,
        'date'
        # optional: 'staff' # this is the name of the assigned person
    ]
    _datetime_columns = ['date']

    events = []
    medications = []
    staffing_records = []

    def __init__(self, *args, **kwargs):
        """
        Expects first argument to be a pandas DataFrame or compatible rectangular data object
        containing at least an 'assignment' and 'date' column. Date column must be castable
        as datetime values.

        In practice, will often have a 'staff' column as well, naming the assigned person.
        """
        super().__init__(*args, **kwargs)

    def generate_activity_from_ps_dict(self, ps_dict):
        """
        Helper function to populate an ActivityDataset using assignment data in
        this object and a dictionary of ProviderShift objects to translate them.

        """

        staffing_slots = []

        for i, assignment in self._df.iterrows():
            s = utils.matching_ps_from_dictionary(assignment['assignment'], ps_dict)
            if s:
                d = assignment['date']
                slot = {
                    'activity_start': d + s.start,
                    'activity_end': d + s.start + s.duration,
                    'activity': s.label,
                    'personnel': assignment['staff'],
                    'capacity': s.capacity
                }
                staffing_slots.append(slot)

        return ActivityDataSet(staffing_slots)

    def limit_to_ps_in_dict(self, ps_dictionary):
        """
        Filters this data down to just those whose assignment value is present
        in the keys of a dictionary, presumably (but not necessarily) one whose
        values are ProviderShift objects
        :param ps_dictionary:
        :return:
        """
        return self.limit_by_list('assignment', ps_dictionary.keys())

    def _generate_capacity_slots(self, provider_shift_dict, resolution='1Min'):
        slots = []
        [
            slots.extend(provider_shift_dict[r['assignment']].dump_slots_as_dicts(r['date'], resolution))
            for i, r in self.iterrows()
        ]
        return slots

    def generate_capacity_tsds(self, provider_shift_dict, start_dt=None, end_dt=None, fillna=0, freq='1Min'):
        """
        Use this DataSet and a dictionary of ProviderShift objects to "translate"
        assignments into capacity at each moment in time, to a resolution of
        freq. Subsequently reshape the data and return it in a CapacityTSDS
        (aka TimeSeriesDataSet) for further use.

        :param provider_shift_dict:
        :param start_dt:
        :param end_dt:
        :param fillna:
        :param freq:
        :return:
        """
        data = pd.DataFrame(
            pd.DataFrame(self._generate_capacity_slots(
                provider_shift_dict, freq
            )).groupby(['datetime_slot'])['capacity'].sum()
        )
        return TimeSeriesDataSet(data=data, start_dt=start_dt, end_dt=end_dt, freq=freq, fillna=fillna)
