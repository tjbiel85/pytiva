from .AnesthesiaDataSet import AnesthesiaDataSet


class AnesthesiaCaseDataSet(AnesthesiaDataSet):
    """
    expected columns:
        * a required admission or encounter ID
        * anesthesia start datetime
        * anesthesia end datetime
        * procedure

    * optional but frequent stuff?
        * patient ID
        * location
        * department name
        * responsible provider ID

    attributes to hold
        * events
        * medications
        * staffing records
    """

    _required_columns = [
        'case_id',
        'anesthesia_start',
        'anesthesia_end',
        'procedure'
    ]
    _datetime_columns = ['anesthesia_start', 'anesthesia_end']

    events = []
    medications = []
    staffing_records = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
