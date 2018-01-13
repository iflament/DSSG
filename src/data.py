from collections import namedtuple
import utils
import pandas as pd
from config import constants, logger_config, _export_dir
import logging
import logging.config

logger = logging.getLogger(__name__)


class DataHandler:
    """Load data and params"""

    logging.config.dictConfig(logger_config)

    def __init__(self):

        # TODO: if file exists locally or in cache, don't read in again!
        self.params_file = constants.PARAMS_FILE
        self.params = self._load_params()

    def _read_yaml(self):
        """Get data from yaml"""

        return utils.read_yaml(self.params_file)

    def _load_params(self):
        """Load in data from yaml"""

        params = self._read_yaml()
        d = dict(params)
        logger.info(d.keys())
        return namedtuple('Params', d.keys())(**d)

    def _get_data(self, query):
        """Get data from DB"""

        df = pd.read_sql(query, con=self.db_connection)

        return df

