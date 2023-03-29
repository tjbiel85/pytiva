from .AnesthesiaDataSet import AnesthesiaDataSet
from ..activity import ActivityDataSet

_MED_DOSE_UNIT = [
    'g',
    'grams',
    'mg',
    'milligrams',
    'mcg',
    'micrograms',
    'ml',
    'milliliters',
    'l',
    'liters',
    'u',
    'Units',
    'patch',
    'puff',
    'tablet',
    'mEq',
    'Million Units (MU)',
    'parts per million (PPM)',
    'inch',
    'suppository',
    'spray'
]

_MED_DOSE_INFUSION_MASS = [
    'kg',
    'kilogram'
]

_MED_DOSE_INFUSION_TIME = [
    'hr',
    'hour',
    'min',
    'minute',
    's',
    'second'
]

MED_UNIT_NAME_ALL = [
    x.lower() for x in _MED_DOSE_UNIT + [
    f'{u}/{m}/{t}' for u in _MED_DOSE_UNIT
                   for m in _MED_DOSE_INFUSION_MASS
                   for t in _MED_DOSE_INFUSION_TIME
    ] + [
    f'{u}/{t}' for u in _MED_DOSE_UNIT
        for t in _MED_DOSE_INFUSION_TIME
    ]
]


MED_ROUTE_NAME_ALL = [x.lower() for x in [
    'cervical',
    'epidural',
    'infiltration',
    'inhalation',
    'injection',
    'intradermal',
    'intramuscular',
    'intrathecal',
    'intravenous',
    'oral',
    'peri-neural',
    'rectal',
    'subcutaneous',
    'sublingual',
    'topical',
    'tracheal tube',
    'transdermal',
    'vaginal',
    'buccal',
    'in vitro',
    'each nare',
    'intra-nasal',
    'intrauterine',
    'both eyes',
    'other',
    'laryngotracheal',
    'intratracheal',
    'nebulization'
]]


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
    _route_label = 'med_route'
    _unit_label = 'med_unit'
    _amount_label = 'med_amount'
    _datetime_label = 'med_datetime'
    _name_label = 'med_name'
    _signature_label = 'med_signature'

    _required_columns = [
        'case_id',
        _name_label,
        _datetime_label,
        _amount_label,
        _unit_label,
        _route_label
    ]

    _datetime_columns = [
        _datetime_label
    ]

    _prohibited_columns = [_signature_label]

    _allowed_routes = [r.lower() for r in MED_ROUTE_NAME_ALL]
    _allowed_units = [u.lower() for u in MED_UNIT_NAME_ALL]

    def __init__(self, data, force_units_to_lower=True, force_routes_to_lower=True,
                 populate_sigs=False, *args, **kwargs):
        super_init_return_val = super().__init__(data=data, *args, **kwargs)

        if force_units_to_lower:
            self._df[self._unit_label] = self._df[self._unit_label].apply(lambda x: str(x).lower())

        if force_routes_to_lower:
            self._df[self._route_label] = self._df[self._route_label].apply(lambda x: str(x).lower())

        if not all(self._df[self._unit_label].isin(self._allowed_units)):
            units_okay_mask = self._df[self._unit_label].isin(self._allowed_units)
            prohibited_units = self._df[ ~units_okay_mask ][self._unit_label].unique()

            raise Exception(f'Prohibited unit label(s) found {[p for p in prohibited_units]}')

        if not all(self._df[self._route_label].isin(self._allowed_routes)):
            routes_okay_mask = self._df[self._route_label].isin(self._allowed_routes)
            prohibited_routes = self._df[ ~routes_okay_mask ][self._route_label].unique()
            raise Exception(f'Prohibited route label found {[p for p in prohibited_routes]}')

        if populate_sigs:
            self._df[self._signature_label] = self._signature_series()

        pass

    def to_activity_dataset(self,
                            offset_before,
                            offset_after,
                            activity_label='medication',
                            *args,
                            **kwargs):

        data = self._with_timespans(
            datetime_col='med_datetime',
            td_offset_before=offset_before,
            td_offset_after=offset_after
        )
        data['activity'] = activity_label
        return ActivityDataSet(data[['activity', 'activity_start', 'activity_end', 'case_id']], *args, **kwargs)

    def _signature_series(self):
        """
        Generate a medication signature for the administered medication.
        :return:
        """
        return self._df.apply(
            lambda x: f'{x[self._name_label]} {x[self._amount_label]} {x[self._unit_label]} {x[self._route_label]}',
            axis=1
        )
