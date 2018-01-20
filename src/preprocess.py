import pandas as pd
from config import constants, logger_config, _export_dir
import logging
import logging.config
import numpy as np
from utils import timeit
from pandas_schema import Column, Schema
from pandas_schema.validation import IsDtypeValidation, DateFormatValidation

logger = logging.getLogger(__name__)


class MuseumDataPreProcess:
    """PreProcess FirenzeCard data"""

    logging.config.dictConfig(logger_config)

    def __init__(self, params, museum_raw_data):

        self.params = params
        self.raw_data = museum_raw_data
        self.validate()

    def validate(self):

        museum_schema = Schema([
            Column('user_id', [IsDtypeValidation(int)]),
            Column('latitude', [IsDtypeValidation(float)]),
            Column('longitude', [IsDtypeValidation(float)]),
            Column('museum_name', [IsDtypeValidation(str)]),
            Column('museum_id', [IsDtypeValidation(int)]),
            Column('short_name', [IsDtypeValidation(str)]),
            Column('total_adults', [IsDtypeValidation(int)]),
            Column('minors', [IsDtypeValidation(int)])
        ])

        errors = museum_schema.validate(self.raw_data)
        logger.info(errors)

        for error in errors:
            logger.info(error)

        return None

    def _extract_features(self):
        """ Feature extraction for FirenzeCard data """

        logger.info('Running feature extraction... ')
        df = self.raw_data

        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['time'] = pd.to_datetime(df['entry_time']).dt.time
        df['date'] = pd.to_datetime(df['entry_time']).dt.date
        df['hour'] = pd.to_datetime(df['entry_time']).dt.hour
        df['day_of_week'] = df['entry_time'].dt.dayofweek

        df = df.sort_values('entry_time', ascending=True)
        df['total_people'] = df['total_adults'] + df['minors']

        df = df.sort_values('entry_time', ascending=True)
        df['total_duration_card_use'] = df[df.user_id.notnull()].groupby(
            'user_id')['entry_time'].transform(lambda x: x.iat[-1] - x.iat[0])
        df['total_duration_card_use'] = df['total_duration_card_use'].apply(
            lambda x: pd.Timedelta(x) / pd.Timedelta('1 hour'))

        df['entry_is_adult'] = np.where(df['total_adults'] == 1, 1, 0)
        df['is_card_with_minors'] = np.where(df['minors'] == 1, 1, 0)

        entrances_per_card_per_museum = pd.DataFrame(df.groupby('user_id', as_index=True)['museum_id'].
                                                     value_counts().rename('entrances_per_card_per_museum'))

        df = pd.merge(entrances_per_card_per_museum.reset_index(), df, on=['user_id', 'museum_id'], how='inner')

        for n in range(1, df['museum_id'].nunique()):
            df['is_in_museum_' + str(n)] = np.where(df['museum_id'] == n, 1, 0)

        if constants.export_to_csv:
            df.to_csv(f'{_export_dir}_museumdata_feature_extracted.csv', index=False)

        return df


class CDRPreProcess:
    """ Preprocess CDR data """

    def __init__(self, params, cdr_raw_data):

        self.params = params
        self.raw_data = cdr_raw_data
        self.validate()
        self.data_feature_extracted = self._extract_features(self.raw_data)

    def validate(self):

        cdr_schema = Schema([
            Column('user_id', [IsDtypeValidation(int)]),
            Column('latitude', [IsDtypeValidation(float)]),
            Column('longitude', [IsDtypeValidation(float)]),
            Column('user_origin', [IsDtypeValidation(str)]),
            Column('in_city_boundaries', [IsDtypeValidation(str)]),
            Column('date_time', [DateFormatValidation(str)]),
            Column('tower_id', [IsDtypeValidation(int)])
        ])

        errors = cdr_schema.validate(self.raw_data)
        logger.info(errors)

        return None

    @timeit(logger)
    def _extract_features(self, data):
        """ Feature Extraction of CDR data """

        # filter out customers that were not in florence city
        mask = ((self.params.lat_min >= data.lat) & (data.lat >= self.params.lat_max) &
                (self.params.lon_min >= data.lon) & (data.lon >= self.params.lon_max))
        df = data.loc[mask]

        # add new column is bot
        calls = pd.DataFrame(df.groupby('cust_id').size()).reset_index('cust_id')
        calls.columns = ['cust_id', 'total_calls']
        df = calls.merge(df, on='cust_id')

        # separate date and time
        df['date'] = pd.to_datetime(df['date_time_m']).dt.date
        df['time'] = pd.to_datetime(df['date_time_m']).dt.time

        df['days_active'] = df.groupby('cust_id')['date'].transform(lambda x: x.iat[-1] - x.iat[0])
        df['days_active'] = df['days_active'].apply(
            lambda x: pd.Timedelta(x) / pd.Timedelta('1 days'))

        # filter out bots
        df['is_bot'] = (df['total_calls'] / df['days_active']) > self.params.bot_threshold
        df = df[df['is_bot'] == False]

        # filter out customers who made less than N calls in florence
        calls_in_florence = df.groupby('cust_id', as_index=False)['in_florence_comune'].sum()
        calls_in_florence.columns = ['cust_id', 'total_calls_in_florence']
        df = df.merge(calls_in_florence, on='cust_id')
        df = df[df['total_calls_in_florence'] > self.params.minimum_calls_in_fc]

        # enough_florence_daily_calls: filter out anyone whose min number daily calls > N
        daily_calls = df.groupby(['cust_id', 'date']).size().reset_index()
        daily_calls.columns = ['cust_id', 'date', 'min_daily_calls']
        daily_calls = daily_calls.groupby('cust_id', as_index=False)['min_daily_calls'].min()

        df = df.merge(daily_calls, on=['cust_id'])
        df = df[df['min_daily_calls'] > self.params.minimum_daily_calls].reset_index()

        if constants.export_to_csv:
            df.to_csv(f'{_export_dir}_cdrdata_feature_extracted.csv', index=False)

        return df



