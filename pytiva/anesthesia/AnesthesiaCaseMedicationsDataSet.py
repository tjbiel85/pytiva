from .AnesthesiaDataSet import AnesthesiaDataSet


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
