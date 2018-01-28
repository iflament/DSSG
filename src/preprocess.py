import pandas as pd
from config import constants, logger_config, _data_dir
import logging
import logging.config
import numpy as np
from utils import timeit

logger = logging.getLogger(__name__)


class MuseumDataPreProcess:
    """PreProcess FirenzeCard data"""

    logging.config.dictConfig(logger_config)

    def __init__(self, click_params, params, site_raw_data):

        self.click_params = click_params
        self.params = params
        self.raw_data = site_raw_data
        self.data_feature_extracted = self._extract_features()

    def _extract_features(self):
        """ Feature extraction for Museum data """

        logger.info('Running museum data feature extraction... ')
        df = self.raw_data

        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['time'] = pd.to_datetime(df['entry_time']).dt.time
        df['date'] = pd.to_datetime(df['entry_time']).dt.date
        df['hour'] = pd.to_datetime(df['entry_time']).dt.hour
        df['day_of_week'] = df['entry_time'].dt.dayofweek

        # create site_id from site_name
        df['site_id'] = df.site_name.apply(lambda x: hash(x))

        df = df.sort_values('entry_time', ascending=True)
        df['total_people'] = df['total_adults'] + df['minors']

        df = df.sort_values('entry_time', ascending=True)
        df['total_duration_card_use'] = df[df.user_id.notnull()].groupby(
            'user_id')['entry_time'].transform(lambda x: x.iat[-1] - x.iat[0])
        df['total_duration_card_use'] = df['total_duration_card_use'].apply(
            lambda x: pd.Timedelta(x) / pd.Timedelta('1 hour'))

        df['entry_is_adult'] = np.where(df['total_adults'] == 1, 1, 0)
        df['is_card_with_minors'] = np.where(df['minors'] == 1, 1, 0)

        entrances_per_card_per_museum = pd.DataFrame(df.groupby('user_id', as_index=True)['site_id'].
                                                     value_counts().rename('entrances_per_card_per_site'))

        df = pd.merge(entrances_per_card_per_museum.reset_index(), df, on=['user_id', 'site_id'], how='inner')

        for n in range(1, df['site_id'].nunique()):
            df['is_in_site_' + str(n)] = np.where(df['site_id'] == n, 1, 0)

        if self.click_params.export:
            df.to_csv(f'{constants.site_output_data}', index=False)

        return df


class CDRPreProcess:
    """ Preprocess CDR data """

    def __init__(self, click_params, params, cdr_raw_data):

        self.click_params = click_params
        self.params = params
        self.raw_data = cdr_raw_data
        self.data_feature_extracted = self._extract_features()

    @timeit(logger)
    def _extract_features(self):
        """ Feature Extraction of CDR data """

        logger.info('Running cdr data feature extraction... ')

        # filter out customers that were not in the city
        df = self.raw_data
        mask = ((self.params.lat_min >= df.latitude) & (df.latitude >= self.params.lat_max) &
                (self.params.lon_min >= df.longitude) & (df.longitude >= self.params.lon_max))
        df = df.loc[mask]
        # df = self.raw_data
        # df = df[df['in_city'] == True]

        calls = pd.DataFrame(df.groupby('user_id', as_index=False).size().reset_index())
        calls.columns = ['user_id', 'total_calls']
        df = calls.merge(df, on='user_id')

        df['date'] = pd.to_datetime(df['date_time_m']).dt.date
        df['rounded_time'] = pd.to_datetime(df['date_time_m']).dt.hour
        df['time'] = pd.to_datetime(df['date_time_m']).dt.time

        days_active = df.groupby('user_id', as_index=False)['date'].count()
        days_active.columns = ['user_id', 'days_active']
        df = df.merge(days_active, on='user_id')

        # filter out bots
        df['is_bot'] = (df['total_calls'] / df['days_active']) > self.params.bot_threshold
        df = df[df['is_bot'] == False]

        # filter out customers who made less than N calls
        calls_in_florence = df.groupby('user_id', as_index=False)['total_calls'].count()
        users_to_keep = list(calls_in_florence[calls_in_florence['total_calls'] >= self.params.minimum_total_calls]['user_id'])
        df = df[df['user_id'].isin(users_to_keep)]

        if self.click_params.export:
            df.to_csv(f'{constants.cdr_output_data}', index=False)

        return df





