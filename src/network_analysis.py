import pandas as pd
from config import constants, logger_config, _data_dir
import logging.config
import logging
import credentials
import plotly
from sankey import Sankey

plotly.tools.set_credentials_file(username=credentials.plotlyu, api_key=credentials.plotlykey)
logger = logging.getLogger(__name__)


class NetworkAnalysis:

    """ Network Analysis """

    logging.config.dictConfig(logger_config)

    def __init__(self, params, data):

        self.params = params
        self.data = data
        # out of the people who do transition within a timedelta, where do they come from, and go to next?
        sankey = Sankey()
        self.plot_url = sankey.plot_sankey()



