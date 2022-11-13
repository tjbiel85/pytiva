import pandas as pd


class DataSet(object):
    """
    A base class for building objects based mostly on pandas.DataFrame
    objects, but with extra functionality one might want to pass forward.

    Acts like a DataFrame except when methods and attributes have been
    defined directly on this object.
    """

    # these need to be set ahead of time in order to let them be handled
    # properly in __init__() without running afoul of getattr/setattr logic
    _df = None
    _required_columns = []
    _datetime_columns = []

    def __init__(self, data, index_column=None, *args, **kwargs):
        if data is None:
            raise Exception(f'data cannot be None')

        # instantiate and keep a pandas DataFrame using supplied data
        try:
            self._df = pd.DataFrame(data, *args, **kwargs).copy()
        except Exception as e:
            print(e)
            raise Exception(f'Supplied data and signature must be able to create a pandas DataFrame')

        # verify required columns, if any, are present
        check, missing_required_columns = self._check_required_columns()
        if not check:
            raise Exception(
                f'This DataSet requires columns {self._required_columns} and is missing {missing_required_columns}')

        for dtc in self._datetime_columns:
            self._df[dtc] = pd.to_datetime(self._df[dtc])

        # if specified, index the DataFrame to the specified column
        if index_column is not None:
            try:
                self._df.set_index(index_column, inplace=True)
            except Exception as e:
                raise Exception(f'an index_column value ({index_column}) was supplied, but could not be set')

    def __getattr__(self, name):
        """
        According to the docs, this should only be triggered if self.__getattribute__()
        has already come up empty. So it should only have to handle finding the attribute
        in the held DataFrame. (This does appear to be the case in testing.)
        """

        try:
            return getattr(self._df, name)
        except Exception as e:
            raise AttributeError(f'Neither {self} nor DataFrame in self._df contain {name}')

    def __setattr__(self, name, value):
        """
        Overrides default setattr to involve the held DataFrame.

        Resolves thusly:
        1) if self.name exists, set that to value
        2) else if self._df.name exists, set that to value
        3) else set self.name to value
        """

        if name in dir(self):
            # hasattr(self, name) cannot be used reliably, because the way python
            # checks to see if an object has an attribute is by attempting to
            # retrieve it, and that would trigger the getattr logic above
            super().__setattr__(name, value)

        elif self._df is not None and name in dir(self._df):
            self._df.__setattr__(name, value)

        else:
            super().__setattr__(name, value)

        pass

    def __getitem__(self, key):
        """
        Overrides default getitem in order to pass along to held DataFrame.
        """
        try:
            # first, look to see if you can do that on this object
            return super().__getitem__(key)

        except AttributeError as e:
            # most likely a non subscriptable object, so head to the held DataFrame
            return self._df[key]

        except IndexError as e:
            # perhaps this is a subscriptable object, but the requested key is not
            # in the index
            # head to the held DataFrame for this, too
            return self._df[key]

    def _check_required_columns(self):
        """
        Helper method to verify whether the supplied data satisfies the required columns.
        """
        missing = []
        check = all([rc in self.columns for rc in self._required_columns])
        if not check:
            for rc in self._required_columns:
                if rc not in self.columns:
                    missing.append(rc)

        return check, missing

    def validate_column(self, column, func):
        """
        Applies the supplied function func element-wise to specified column. The
        column is considered valid if every element returns True using func(element).
        """
        return all(self._df[column].apply(func))
