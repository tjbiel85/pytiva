from ..dataset import DataSet


class StaffingDataSet(DataSet):
    """
    Child class for making DataSet objects specific to staffing data concerns.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
