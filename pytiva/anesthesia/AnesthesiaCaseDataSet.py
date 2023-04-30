import operator

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

    _excluded_procedures = []
    _excluded_locations = []

    _required_columns = [
        'case_id',
        'anesthesia_start',
        'anesthesia_end',
        'procedure'
    ]
    _datetime_columns = ['anesthesia_start', 'anesthesia_end']
    _str_columns = ['location']

    events = []
    medications = []
    staffing_records = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def limit_by_procedure_list(self, lst_procedures, case_sensitive=False):
        """
        Limit the cases by procedure value using a list of permissible procedures.

        Returns *excluded* items.
        """

        if case_sensitive:
            lst_filter = lst_procedures
            proc_mask = self._df['procedure'].apply(lambda x: x in lst_filter)
        else:
            lst_filter = [p.lower() for p in lst_procedures]
            proc_mask = self._df['procedure'].apply(lambda x: str(x).lower() in lst_filter)

        ds_excluded = self._self_type(self._df.loc[~proc_mask])
        self._excluded_procedures.extend(ds_excluded['procedure'].unique())

        self._df = self._df.loc[proc_mask]
        return ds_excluded

    def limit_by_location_list(self, lst_locations, case_sensitive=False):
        """
        Limit the cases by location value using a list of permissible procedures.

        Returns *excluded* items.
        """

        if case_sensitive:
            lst_filter = lst_locations
            loc_mask = self._df['location'].apply(lambda x: x in lst_locations)
        else:
            lst_filter = [p.lower() for p in lst_locations]
            loc_mask = self._df['location'].apply(lambda x: str(x).lower() in lst_filter)

        ds_excluded = self._self_type(self._df.loc[~loc_mask])
        self._excluded_locations.extend(ds_excluded['location'].unique())

        self._df = self._df.loc[loc_mask]
        return ds_excluded

    def limit_anesthesia_start_by_datetime(self, dt_bound, lower_bound=True, inclusive=True):
        """
        Limit the cases by anesthesia_start using a pandas DateTime object.

        By default, a lower (left) bound and inclusive of the bound itself.
        """

        if lower_bound:
            if inclusive:
                o = operator.ge
            else:
                o = operator.gt

        else:
            if inclusive:
                o = operator.le
            else:
                o = operator.lt

        self._df = self._df.loc[o(dt_bound, self._df['anesthesia_start'])]
        pass
