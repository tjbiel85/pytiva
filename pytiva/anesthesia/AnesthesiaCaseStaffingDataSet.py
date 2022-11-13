from .AnesthesiaDataSet import AnesthesiaDataSet


class AnesthesiaCaseStaffingDataSet(AnesthesiaDataSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
