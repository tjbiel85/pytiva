import pandas as pd
from ..activity import ActivityDataSet
from ..anesthesia.EventActivityDefinition import EventActivityDefinition


class AnesthesiaStudy(object):
    # initialize some attributes as NoneTypes by default
    ds_activity = None
    _unduplicated_activity = None
    _unduplicated_concurrency = None
    _allowed_member_case_datasets = [
        'ds_cases',
        'ds_case_events',
        'ds_case_meds',
        'ds_case_staffing'
        #'ds_resources'
    ]

    _config_labels = { # these are a mess, but good enough for now
        'cases_section': 'CASE_LIMITS',
        'case_date_range': 'ANESTHESIA_START_RANGE',
        'case_locations_key': 'LOCATIONS',
        'case_procedures_key': 'PROCEDURES',
        'activity_section': 'ACTIVITIES',
        'meds_td_before': 'MEDICATION_ACTIVITY_OFFSET_BEFORE',
        'meds_td_after':'MEDICATION_ACTIVITY_OFFSET_AFTER',
        'event_definitions': 'EVENT_ACTIVITY_DEFINITIONS'
    }

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
        return [x for x in self._allowed_member_case_datasets if
                hasattr(self, x) and getattr(self, x) is not None]

    @property
    def _case_dataset_member_dict(self):
        return {n: getattr(self, n) for n in self._case_dataset_member_names}

    def _propagate_member_cases(self, cases_from='ds_cases', include_activity=True):
        """
        Limit the member case DataSets by the case_id values in ds_case.

        By default, propagates cases from ds_cases, but can propagate them to everybody else if a different
        DataSet is specified.
        """

        if cases_from not in self._allowed_member_case_datasets:
            raise Exception(f'cases_from must be in {self._allowed_member_case_datasets} (got "{cases_from}")')

        allowed = getattr(self, cases_from)['case_id'].unique()

        for name, ds in self._case_dataset_member_dict.items():
            new_ds = ds._self_type(ds.loc[ds['case_id'].isin(allowed)])
            setattr(self, name, new_ds)

        # TODO: refactor this more elegantly somehow, ?integrate elsewhere
        if include_activity and self.ds_activity is not None:
            self.ds_activity._df = self.ds_activity._df[
                self.ds_activity._df['case_id'].isin(self.ds_cases['case_id'].tolist())]

        pass

    def limit_by_list(self, target_col, lst_items, ds_label='ds_cases',
                      return_excluded=True, propagate_cases=True):

        if ds_label not in self._allowed_member_case_datasets:
            raise Exception(f'member_dataset must be in {self._allowed_member_case_datasets} (got "{ds_label}")')

        ds_excluded = getattr(self, ds_label).limit_by_list(target_col, lst_items)

        if propagate_cases:
            self._propagate_member_cases(cases_from=ds_label)

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

    @property
    def _member_ds_and_counts(self):
        # in which case, unittests will need to be updated to support them
        # (json casts tuples to list, which is how the data are stored for comparison)
        return [[k, len(v._df)] for k, v in self._case_dataset_member_dict.items()]

    def summarize(self, verbose=True, activity_count_freq='M', extra_quantiles=[.90, .95, .98]):
        lines = [f"### AnesthesiaStudy object ###"]

        # case summary info
        lines.append(f'* Case data *')

        start_min, start_max = self._anesthesia_start_range
        lines.append(f"ds_cases['anesthesia_start'] range: {start_min} to {start_max}")

        members = [lines.append(f"{n} ({ds._length} rows)") for n, ds in self._case_dataset_member_dict.items()]

        if self.ds_activity is not None:
            lines.append(f'\n* Activity data *')
            hr_activity = f'ds_activity: ' + self.ds_activity.hr_activity_summary()
            lines.append(hr_activity)

            if verbose:
                s = self.ds_activity.groupby(['activity', pd.Grouper(key='activity_start', axis=0, freq=activity_count_freq)])[
                    'case_id'].count()
                lines.extend(repr(s).split('\n')[:-1])

                described = self.ds_activity.groupby('activity')['duration'].describe()
                for x in extra_quantiles:
                    described["{0:.0%}".format(x)] = self.ds_activity.groupby('activity')['duration'].quantile(x)

                lines.extend(repr(described[sorted(described.columns)].T).split('\n'))

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

        if self._config_labels['cases_section'] in config_dict.keys():
            case_limits = config_dict[self._config_labels['cases_section']]

            # dates
            if self._config_labels['case_date_range'] in case_limits.keys():
                s, e = case_limits[self._config_labels['case_date_range']]
                self.limit_by_dates(dt_end=pd.to_datetime(e), dt_start=pd.to_datetime(s))

            # procedures
            if self._config_labels['case_procedures_key'] in case_limits.keys():
                self.limit_by_list('procedure', case_limits[self._config_labels['case_procedures_key']])

            # locations
            if self._config_labels['case_locations_key'] in case_limits.keys():
                self.limit_by_list('location', case_limits[self._config_labels['case_locations_key']])

        # activity stuff --> consider moving this to self.generate_activity_ds() somehow
        all_activities = []
        if self._config_labels['activity_section'] in config_dict.keys():
            activities = config_dict[self._config_labels['activity_section']]
            med_activity = None
            event_activity = None

            # from medications!
            # TODO: make this more granular, such as different times for different meds; ?MedicationActivityDefinition?
            if self._config_labels['meds_td_before'] in activities.keys() and self._config_labels['meds_td_after'] in activities.keys():
                med_activity = self.ds_case_meds.to_activity_dataset(
                    offset_before=activities[self._config_labels['meds_td_before']],
                    offset_after=activities[self._config_labels['meds_td_after']]
                )
                all_activities.append(med_activity)

            # from events!
            if self._config_labels['event_definitions'] in activities.keys():
                event_activity = []

                for activity_definition in activities[self._config_labels['event_definitions']]:
                    ead = EventActivityDefinition(**activity_definition)
                    event_activity.append(ead.apply_to_ds(self.ds_case_events))

                all_activities.extend(event_activity)

            # combine them all!
            self.ds_activity = ActivityDataSet(pd.concat(all_activities).drop(columns='duration'))

        return all_activities

    def unduplicate_activity(self, strata=['case_id'], *args, **kwargs):
        """
        Wraps self.ds_activity.fetch_unduplicated_concurrency(), passing along unused arguments.

        By default, unduplicates with case_id as the lone stratum, but could happily use any levels.
        """

        if self.ds_activity is not None:
            self._unduplicated_activity = self.ds_activity.fetch_unduplicated_concurrency(strata=strata,
                                                                                          *args,
                                                                                          **kwargs)
            return self._unduplicated_activity
        else:
            return False

    def unduplicate_concurrency(self, strata=['case_id'], resolution=None, *args, **kwargs):
        """
        Wraps self.unduplicate_activity(), passing along unused arguments.

        By default, unduplicates with case_id as the lone stratum, but could happily use any levels.

        :param strata:
        :param resolution:
        :return:
        """
        unduplicated_activity = self.unduplicate_activity(strata=strata)

        self._unduplicated_concurrency = unduplicated_activity.concurrency_ts(resolution=resolution,
                                                                              *args,
                                                                              **kwargs)
        return self._unduplicated_concurrency

    def __repr__(self):
        return self.summarize(verbose=False)
