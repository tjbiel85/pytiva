from ..dataset import DataSet


class AnesthesiaDataSet(DataSet):
    """
    A parent class for various anesthesia-related DataSet objects to inherit from.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
