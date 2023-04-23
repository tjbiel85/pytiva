from ..dataset import TimeSeriesDataSet


class CapacityTSDS(TimeSeriesDataSet):
    """
    Child class for making TimeSeriesDataSet objects specific to staffing/resource capacity.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
