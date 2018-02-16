import pandas as pd
from config import constants, logger_config, _data_dir
import logging.config
import logging

logger = logging.getLogger(__name__)


class Sankey:

    logging.config.dictConfig(logger_config)

    def __init__(self, df, source='source', target='target', value='total_people', colors=None):

        self.data = self.prepare_data(df)
        self.source = self.data[source]
        self.target = self.data[target]
        self.value = self.data[value]
        self.colors = colors

    @staticmethod
    def prepare_data(df):

        df = df[['user_id', 'total_people', 'site_name']]

        mask = pd.DataFrame(df.groupby(['user_id'], as_index=True).count()['total_people'])
        mask = mask[mask > 1]
        mask = mask.dropna()
        df = df[df.user_id.isin(mask.index)]

        df['target'] = df['site_name']
        df['source'] = df.groupby('user_id')['site_name'].shift(1)
        df = df.dropna()
        keep = (df['target'] != df['source'])
        df = df[keep]

        return df

    def _plot_sankey(self):

        pass