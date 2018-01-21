import logging
from config import constants, logger_config
from data import DataHandler
from preprocess import MuseumDataPreProcess, CDRPreProcess
from museum import MuseumAnalysis
from telecom import CDRAnalysis
from network_analysis import NetworkAnalysis
from fountain_deck_gl import FountainViz
from slack_bot import SlackBot

logger = logging.getLogger(__name__)


def pipeline():

    logging.config.dictConfig(logger_config)

    # ---------------------------------------
    # Get Params and Constants, Load data
    # ---------------------------------------
    nest = DataHandler()

    bot = SlackBot()
    pipeline_run_info = bot.generate_message(nest.input_params)
    bot.send_msg(pipeline_run_info)

    if nest.input_params.museum_data:
        # -----------------------
        # Preprocess Museum data
        # -----------------------
        bot.send_msg('preprocessing museum data...')
        museum_data = MuseumDataPreProcess(
            input_params=nest.input_params,
            analysis_params=nest.analysis_params,
            museum_raw_data=nest.museum_raw_data
        )

        # ---------------------------------------
        # Museum Data Analysis
        # ---------------------------------------
        bot.send_msg('running museum data analysis...')
        MuseumAnalysis(
            params=nest.analysis_params,
            data_feature_extracted=museum_data.data_feature_extracted
        )

        # ---------------------------------------
        # Network Analysis
        # ---------------------------------------
        bot.send_msg('running network analysis...')
        network_analysis = NetworkAnalysis(
            params=nest.analysis_params,
            data=museum_data.data_feature_extracted
        )

        # --------------------------------------------
        # Create Fountain Visualization of museum data
        # --------------------------------------------
        bot.send_msg('building fountain visualization')
        FountainViz(
            network_analysis=network_analysis,
            museum_data=museum_data
        )

    if nest.input_params.cdr_data:
        # --------------------
        # Preprocess Cdr data
        # --------------------
        bot.send_msg('preprocessing cdr data...')
        cdr_data = CDRPreProcess(
            input_params=nest.input_params,
            analysis_params=nest.analysis_params,
            cdr_raw_data=nest.cdr_raw_data
        )

        # ---------------------------------------
        # CDR Data Analysis
        # ---------------------------------------
        bot.send_msg('running cdr analysis...')
        CDRAnalysis(
            params=nest.analysis_params,
            data_feature_extracted=cdr_data.data_feature_extracted
        )

if __name__ == "__main__":
    pipeline()

