import pandas as pd


class ProviderShift(object):
    """Object class to represent a shift for a given provider."""

    def __init__(self, start, duration, label=None, capacity=1.0):
        """
        :param start:  datetime object representing the start of the shift
        :param duration: timedelta object representing the duration of the shift
        :param label: an optional human-readable label describing the shift
        :param capacity: the staffing capacity "weight" of the shift in question; for example, perhaps an attending
            physician is weighted at 1.0, while a trainee might be weighted at a lesser value or even at 0
        """
        self.start = start
        self.duration = duration
        self.label = label
        self.capacity = capacity

    def __repr__(self):
        return f'<ProviderShift: "{self.label}", start={self.start}, duration={self.duration}, capacity={self.capacity}>'

    @property
    def end(self):
        return self.start + self.duration

    def check_time_within_shift(self, comparison,
                                include_left=True,
                                include_right=False):
        if include_left:
            left_compare = self.start <= comparison
        else:
            left_compare = self.start < comparison

        if include_right:
            right_compare = self.end >= comparison
        else:
            right_compare = self.end > comparison

        return left_compare and right_compare

    def shift_td_range(self, frequency, include_right=False):
        r = pd.timedelta_range(
            start=self.start,
            end=self.end,
            freq=frequency
        )
        if include_right:
            return r
        else:
            return r[0:-1]

    def dump_slots_as_dicts(self, index_date, frequency='1H'):
        """
        Output a collection of dictionary objects spanning the entirety of the
        shift, starting with self.start on index_date. The total number of
        objects will be equal to shift duration divided by frequency.

        For example, a ten hour shift and a thirty minute frequency will result
        in 20 objects.

        The supplied frequency must be compatible with generating a timedelta
        range, and defaults to one hour.

        Objects are formatted as:
            {
                label: self.label, (same for entire set)
                index_date: index_date, (same for entire set)
                datetime_slot: generated time slot,
                capacity: self.capacity
            }

        # note: this could be expanded to have a "staffing value" for each slot,
        whereby an attending could count as 0 (for example) in order to
        represent that they are not available to do their own case(s)

        """

        return [{'label': self.label,
                 'index_date': index_date,
                 'datetime_slot': index_date + td,
                 'capacity': self.capacity
                 } for td in self.shift_td_range(frequency)]
