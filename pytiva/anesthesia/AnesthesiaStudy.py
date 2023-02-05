import pandas as pd
from ..activity import ActivityDataSet


class AnesthesiaStudy(object):
    # initialize some attributes as NoneTypes by default
    ds_activity = None
    _unduplicated_activity = None
    _unduplicated_concurrency = None

    def __init__(self,
                 ds_cases,
                 ds_case_events=None,
                 ds_case_meds=None,
                 ds_case_staffing=None,
                 config_dict=None):
        """
        Object to hold and manage interactions between cases, events, and medications within a group of anesthesia
        records data.
        :param ds_cases:
        :param ds_case_events:
        :param ds_case_meds:
        :param ds_case_staffing:
        :param config_dict:
        """

        self.ds_cases = ds_cases
        self.ds_case_events = ds_case_events
        self.ds_case_meds = ds_case_meds
        self.ds_case_staffing = ds_case_staffing

        self._config = config_dict

    @property
    def _case_dataset_member_names(self):
        return [x for x in ['ds_cases', 'ds_case_events', 'ds_case_meds', 'ds_case_staffing'] if
                hasattr(self, x) and getattr(self, x) is not None]

    @property
    def _case_dataset_member_dict(self):
        return {n: getattr(self, n) for n in self._case_dataset_member_names}

    def _propagate_member_cases(self):
        """
        Limit the member case DataSets by the case_id values in ds_case.
        """
        allowed = self.ds_cases['case_id'].unique()

        for name, ds in self._case_dataset_member_dict.items():
            ds_type = ds._self_type
            new_ds = ds_type(ds.loc[ds['case_id'].isin(allowed)])
            setattr(self, name, new_ds)

    def limit_by_procedures(self, lst_procedures, case_sensitive=False,
                            propagate_cases=True, return_excluded=False):
        """
        Limit the cases in ds_cases by procedure value using a list of permissible procedures.

        Updates data in self.ds_cases and returns excluded items.
        """

        ds_excluded = self.ds_cases.limit_by_procedure_list(lst_procedures, case_sensitive)

        if propagate_cases:
            self._propagate_member_cases()

        if return_excluded:
            return ds_excluded

        pass

    def limit_by_dates(self, dt_start, dt_end,
                       start_inclusive=True, end_inclusive=True,
                       propagate_cases=True):
        """
        Helper method to quickly limit an entire AnesthesiaStudy and its member
        DataSets by a supplied date range bound by dt_left_bound and dt_right_bound.

        By default, these are both inclusive.
        """
        self.ds_cases.limit_anesthesia_start_by_datetime(dt_end, inclusive=start_inclusive)
        self.ds_cases.limit_anesthesia_start_by_datetime(dt_start, inclusive=end_inclusive,
                                                         lower_bound=False)

        if propagate_cases:
            self._propagate_member_cases()

        pass

    @property
    def _anesthesia_start_range(self):
        """As tuple
        """
        return self.ds_cases['anesthesia_start'].min(), self.ds_cases['anesthesia_start'].max()

    def summarize(self):
        lines = []
        lines.append(f"## AnesthesiaStudy object ##")

        start_min, start_max = self._anesthesia_start_range
        lines.append(f"ds_cases['anesthesia_start'] range: {start_min} to {start_max}")

        members = [lines.append(f"{n} ({ds._length} rows)") for n, ds in self._case_dataset_member_dict.items()]

        if self.ds_activity is not None:
            hr_activity = f'ds_activity: ' + self.ds_activity.hr_activity_summary()
            lines.append(hr_activity)

        return "\n".join(lines)

    def process_study_config(
            self,
            config_dict,
            extract_activity=True):
        """
        Study is an AnesthesiaStudy object with DataSet objects loaded in already. This is
        modified in place.

        config_dict is something like:

        {
            'CASE_LIMITS': {
                'ANESTHESIA_START_RANGE': ('2021-10-01', '2022-09-30'),
                #'LOCATIONS': [
                #    'AMC LABOR AND DELIVERY',
                #    'ZZ ANESTHESIA',
                #    'AMC EAST PERIOP SVC',
                #    'AMC CNTRAL PERIOP SVC'
                #],
                'PROCEDURES': [
                    'CESAREAN SECTION REPEAT (N/A Abdomen)',
                    'CS',
                    'C Section',
                    'CESAREAN SECTION PRIMARY 1919 (Bilateral )',
                    'CESAREAN SECTION PRIMARY 1919',
                    'CESAREAN SECTION REPEAT WITH BILATERAL TUBAL LIGATION (Bilateral )',
                    'Cesarean Delivery',
                    'CESAREAN SECTION UNDEFINED (N/A )',
                    'CESAREAN SECTION REPEAT',
                    'CESAREAN SECTION REPEAT (N/A )',
                    'REPEAT LOW TRANSVERSE CESAREAN SECTION (N/A )',
                    'BLOOD PATCH',
                    'CESAREAN SECTION REPEAT (Bilateral )',
                    'CESAREAN SECTION (N/A )',
                    'D&E (N/A Uterus)',
                    'REPEAT CESAREAN SECTION (N/A )',
                    'CERVICAL CERCLAGE 1917',
                    'CERVICAL CERCLAGE 1917 (N/A )',
                    'CESAREAN SECTION REPEAT. (N/A )',
                    'EXTERNAL CEPHALIC VERSION',
                    'TUBAL LIGATION/CLIP (WITH CESAREAN SECTION) 2959 (N/A )',
                    'CESAREAN SECTION PRIMARY 1919 (N/A )',
                    'CESAREAN SECTION PRIMARY 1919 (N/A Abdomen)',
                    'LABOR EPIDURAL/ANALGESIA',
                    'DILATATION AND CURETTAGE POST PARTUM (N/A )',
                    'REPAIR VAGINAL TEAR (N/A )',
                    'CESAREAN SECTION REPEAT LOW TRANSVERSE (N/A )',
                    'D&C under regional',
                    'ECV',
                    'INDUCTION',
                    'PPBTL'
                ]
            },
            'ACTIVITIES': {
                'MEDICATION_ACTIVITY_OFFSET_BEFORE': pd.to_timedelta(2, unit='minute'),
                'MEDICATION_ACTIVITY_OFFSET_AFTER': pd.to_timedelta(2, unit='minute'),
                'EVENT_ACTIVITY_DEFINITIONS': [
                    {
                        'LABEL': 'regional procedure',
                        'EVENT_START': 'Link Anesthesia Device',
                        'EVENT_END': 'Block dosed',
                        'MAX_DURATION_QUANTILE': 0.9,
                        'MAX_DURATION_FACTOR': 2
                    },

                    {
                        'LABEL': 'operating room case',
                        'EVENT_START': 'Patient in Room',
                        'EVENT_END': 'Anesthesia Stop',
                        'MAX_DURATION_QUANTILE': 0.95,
                        'MAX_DURATION_FACTOR': 2
                    }
                ]
            }
        }
        """

        _cases_section = 'CASE_LIMITS'
        _case_date_range = 'ANESTHESIA_START_RANGE'
        _case_locations_key = 'LOCATIONS'
        _case_procedures_key = 'PROCEDURES'

        _activity_section = 'ACTIVITIES'
        _meds_td_before = 'MEDICATION_ACTIVITY_OFFSET_BEFORE'
        _meds_td_after = 'MEDICATION_ACTIVITY_OFFSET_AFTER'
        _event_definitions = 'EVENT_ACTIVITY_DEFINITIONS'

        if _cases_section in config_dict.keys():
            case_limits = config_dict[_cases_section]

            # dates
            if _case_date_range in case_limits.keys():
                s, e = case_limits[_case_date_range]
                self.limit_by_dates(dt_end=pd.to_datetime(e), dt_start=pd.to_datetime(s))

            # procedures
            if _case_procedures_key in case_limits.keys():
                self.limit_by_procedures(case_limits[_case_procedures_key])

            # locations
            # TODO

        # activity stuff
        all_activities = []
        if _activity_section in config_dict.keys():
            activities = config_dict[_activity_section]
            med_activity = None
            event_activity = None

            # from medications!
            # TODO: make this more granular, such as different times for different meds
            if _meds_td_before in activities.keys() and _meds_td_after in activities.keys():
                med_activity = self.ds_case_meds.to_activity_dataset(
                    offset_before=activities[_meds_td_before],
                    offset_after=activities[_meds_td_after]
                )
                all_activities.append(med_activity)

            # from events!
            if _event_definitions in activities.keys():
                event_activity = []

                for activity_definition in activities[_event_definitions]:
                    # TODO: consider abstracting this out to a separate activity_from_events() or some such
                    # would like to be able to set aside some info about how these are generated
                    # maybe separate out the initial activity generation versus the truncation for max duration?

                    # print(activity_definition)
                    ds = self.ds_case_events.activity_ds_from_start_and_end_events(
                        start_event=activity_definition['EVENT_START'],
                        end_event=activity_definition['EVENT_END'],
                        activity_name=activity_definition['LABEL']
                    )

                    # truncate using maximum duration criteria
                    maximum_duration = ds['duration'].quantile(activity_definition['MAX_DURATION_QUANTILE']) * \
                                       activity_definition['MAX_DURATION_FACTOR']

                    # print(ds['duration'].describe())
                    # print(f"Duration {activity_definition['MAX_DURATION_QUANTILE']}%ile: {ds['duration'].quantile(activity_definition['MAX_DURATION_QUANTILE'])}")
                    # print(f'Maximum duration by quantile and factor: {maximum_duration}')

                    ds.loc[ds['duration'] > maximum_duration, 'duration'] = maximum_duration
                    event_activity.append(ds)

                all_activities.extend(event_activity)

            # combine them all!
            self.ds_activity = ActivityDataSet(pd.concat(all_activities).drop(columns='duration'))

        return all_activities

    def unduplicate_activity(self, strata=['case_id']):
        """
        By default, unduplicates with case_id as the lone stratum.
        """

        if self.ds_activity is not None:
            self._unduplicated_activity = self.ds_activity.fetch_unduplicated_concurrency(strata=strata)
            return self._unduplicated_activity
        else:
            return False

    def unduplicate_concurrency(self, strata=['case_id'], resolution=None):
        unduplicated_activity = self.unduplicate_activity(strata=strata)

        self._unduplicated_concurrency = unduplicated_activity.concurrency_ts(resolution=resolution)
        return self._unduplicated_concurrency

    def __repr__(self):
        return self.summarize()
