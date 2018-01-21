from collections import namedtuple
import utils
import pandas as pd
from config import constants, logger_config, _data_dir
import logging
import logging.config

logger = logging.getLogger(__name__)


class DataHandler:
    """ Load data and params """

    logging.config.dictConfig(logger_config)

    def __init__(self):

        self.input_params = self._load_params('input_params', constants.INPUT_PARAMS_FILE)
        logger.info(self.input_params)
        self.analysis_params = self._load_params('analysis_params', constants.ANALYSIS_PARAMS_FILE)
        logger.info(self.analysis_params)

        if self.input_params.museum_data:
            if self.input_params.museum_data_input == 'local_file':
                self.museum_raw_data = self._get_data_from_file(constants.museum_input_data)
            elif self.input_params.museum_data_input == 'database':
                self.museum_raw_data = self._get_data_from_db(constants.museum_input_query)

        if self.input_params.cdr_data:
            if self.input_params.cdr_data_input == 'local_file':
                self.cdr_raw_data = self._get_data_from_file(constants.cdr_input_data)
            elif self.input_params.cdr_data_input == 'database':
                self.cdr_raw_data = self._get_data_from_db(constants.cdr_input_query)

    @staticmethod
    def _read_yaml(params_file):
        """ Get params from yaml """

        return utils.read_yaml(params_file)

    def _load_params(self, name, params_file):
        """ Load analysis params from yaml """

        params = self._read_yaml(params_file)
        d = dict(params)
        return namedtuple(name, d.keys())(**d)

    @staticmethod
    def _get_data_from_db(db_connection, query):
        """ Load data from DB """

        df = pd.read_sql(query, con=db_connection)

        return df

    @staticmethod
    def _get_data_from_file(path):
        """ Load data from local file """

        df = pd.read_csv(path, index_col=0)

        return df


