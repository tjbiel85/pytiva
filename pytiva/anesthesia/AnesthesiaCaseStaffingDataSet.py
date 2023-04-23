from .AnesthesiaDataSet import AnesthesiaDataSet


class AnesthesiaCaseStaffingDataSet(AnesthesiaDataSet):
    """
    Placeholder intended to (potentially) manage data of staff signed in to cases.

    This is *not* the representation of staff schedules or available resources.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
