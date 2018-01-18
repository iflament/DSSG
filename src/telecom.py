import pandas as pd
import numpy as np
import plotly
from config import constants, logger_config, _export_dir
import logging.config
import logging
import credentials

plotly.tools.set_credentials_file(username=credentials.plotlyu, api_key=credentials.plotlykey)
logger = logging.getLogger(__name__)


class CDRAnalysis:
    """CDR Analysis"""

    logging.config.dictConfig(logger_config)

    def __init__(self, params, data_feature_extracted):
        self.params = params
        self.data_feature_extracted = data_feature_extracted
        self.cdr_main(self.data_feature_extracted)

    @staticmethod
    def cdr_main(df):
        """ Exploratory analysis of CDR data """

        # Create a frequency count of how many average  daily calls each customer makes
        daily_calls = df.groupby(['cust_id', 'date'], as_index=False).count()

        # Create a frequency count of how many average hourly calls each customer makes
        hourly_calls = df.groupby(['cust_id', 'time'], as_index=False).count()

        # Count calls per customer
        calls_per_cust = df.groupby(['cust_id'], as_index=False).count()

        # Total estimated daily presences: Italians & Foreigners
        # Make a stacked bar plot day by day through summer

        # Estimated daily presence of foreign visitors

        # Estimated daily presence of Italian visitors

        # Duration of stay of foreign visitors

        # Duration of stay of Italian visitors

        return None













