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

    def __init__(self, city, slackbot, export, sitedata, sitedata_format, cdrdata, cdrdata_format, net_analysis, vis,
                       sampling, sample_size):

        self.city = city
        self.slackbot = city
        self.export = export
        self.sitedata = sitedata
        self.sitedata_format = sitedata_format
        self.cdrdata = cdrdata
        self.cdrdata_format = cdrdata_format
        self.net_analysis = net_analysis
        self.vis = vis
        self.sampling = sampling
        self.sample_size = sample_size
        self.click_params, self.params = self._load_params(constants.ANALYSIS_PARAMS_FILE)

        if self.sitedata:
            if self.sitedata_format == 'local_file':
                self.site_raw_data = self._get_data_from_file(constants.site_input_data)
            elif self.sitedata_format == 'database':
                self.site_raw_data = self._get_data_from_db(constants.site_input_query)

        if self.cdrdata:
            if self.cdrdata_format == 'local_file':
                self.cdr_raw_data = self._get_data_from_file(constants.cdr_input_data)
            elif self.cdrdata_format == 'database':
                self.cdr_raw_data = self._get_data_from_db(constants.cdr_input_query)

    @staticmethod
    def _read_yaml(params_file):
        """ Get params from yaml """

        return utils.read_yaml(params_file)

    def _load_params(self, params_file):
        """ Load analysis params from yaml """

        params = self._read_yaml(params_file)
        p = dict(params)

        click_p = dict()
        click_p['city'] = self.city
        click_p['slackbot'] = self.slackbot
        click_p['export'] = self.export
        click_p['sitedata'] = self.sitedata
        click_p['sitedata_format'] = self.sitedata_format
        click_p['cdrdata'] = self.cdrdata
        click_p['cdrdata_format'] = self.cdrdata_format
        click_p['net_analysis'] = self.net_analysis
        click_p['vis'] = self.vis
        click_p['sampling'] = self.sampling
        click_p['sample_size'] = self.sample_size

        return namedtuple('Click_params', click_p.keys())(**click_p), namedtuple('Params', p.keys())(**p)

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


