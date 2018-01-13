import logging
from config import constants, logger_config
from data import DataHandler
from preprocess import MuseumDataPreProcess, CDRPreProcess
from museum import MuseumAnalysis
from telecom import CDRAnalysis
from network_analysis import NetworkAnalysis

logger = logging.getLogger(__name__)


def florence_pipeline():

    logging.config.dictConfig(logger_config)

    # ---------------------------------------
    # Get Params and Constants
    # ---------------------------------------
    nest = DataHandler()
    params_file = constants.PARAMS_FILE
    params = nest._load_params()

    # -----------------
    # Check data format
    # -----------------

    # ---------------------------------------
    # Preprocess Data
    # ---------------------------------------
    museums_data = MuseumDataPreProcess(params=params)
    cdr_data = CDRPreProcess(params=params,
                             museum_data=museums_data.fc_locations_data)

    # Run Situation Analyses on Museum and CDR data...
    # ---------------------------------------
    # Museum Data Analysis
    # ---------------------------------------
    MuseumAnalysis(
        params=params,
        museum_data=museums_data.fc_data
    )

    # ---------------------------------------
    # CDR Data Analysis
    # ---------------------------------------
    CDRAnalysis(
        params=params,
        cdr_data=cdr_data
    )

    # ---------------------------------------
    # Museum Network Analysis
    # ---------------------------------------
    NetworkAnalysis(
        params=params,
        data=museums_data.fc_data
    )


if __name__ == "__main__":
    florence_pipeline()

