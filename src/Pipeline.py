import logging
from config import constants, logger_config
from data import DataHandler
from preprocess import MuseumDataPreProcess, CDRPreProcess
from museum import MuseumAnalysis
from telecom import CDRAnalysis
from network_analysis import NetworkAnalysis
from fountain_deck_gl import FountainViz
from bot import SlackBot
import click

logger = logging.getLogger(__name__)

@click.command()
@click.option('--export', is_flag=True, default=True)
@click.option('--sitedata', is_flag=True, default=True)
@click.option('--sitedata_format', type=str, default="local_file")
@click.option('--cdrdata', is_flag=True, default=True)
@click.option('--cdrdata_format', type=str, default="local_file")
@click.option('--net_analysis', is_flag=True, default=False)
@click.option('--vis', is_flag=True, default=False)
@click.option('--sampling', is_flag=True, default=False)
@click.option('--sample_size', type=int, default=1000)
def pipeline(export, sitedata, sitedata_format, cdrdata, cdrdata_format, net_analysis, vis,
             sampling, sample_size):

    logging.config.dictConfig(logger_config)

    # ---------------------------------------
    # Get Params and Constants, Load data
    # ---------------------------------------
    nest = DataHandler(export, sitedata, sitedata_format, cdrdata, cdrdata_format, net_analysis, vis,
                       sampling, sample_size)

    bot = SlackBot()
    bot.send_msg(f' :cityscape: Cityflows test run \n '
                 f'{nest.click_params} \n\n ')

    if nest.click_params.sitedata:
        # -----------------------
        # Preprocess Museum data
        # -----------------------
        bot.send_msg('Preprocessing museum data...')
        museum_data = MuseumDataPreProcess(
            click_params=nest.click_params,
            params=nest.params,
            museum_raw_data=nest.museum_raw_data
        )

        # ---------------------------------------
        # Museum Data Analysis
        # ---------------------------------------
        bot.send_msg('Running museum data analysis...')
        MuseumAnalysis(
            params=nest.params,
            data_feature_extracted=museum_data.data_feature_extracted
        )

        # ---------------------------------------
        # Network Analysis
        # ---------------------------------------
        bot.send_msg('Running network analysis...')
        network_analysis = NetworkAnalysis(
            params=nest.params,
            data=museum_data.data_feature_extracted
        )

        # --------------------------------------------
        # Create Fountain Visualization of museum data
        # --------------------------------------------
        bot.send_msg('Building fountain visualization')
        FountainViz(
            network_analysis=network_analysis,
            museum_data=museum_data
        )

    if nest.click_params.cdrdata:
        # --------------------
        # Preprocess Cdr data
        # --------------------
        bot.send_msg('Preprocessing cdr data...')
        cdr_data = CDRPreProcess(
            params=nest.params,
            cdr_raw_data=nest.cdr_raw_data
        )

        # ---------------------------------------
        # CDR Data Analysis
        # ---------------------------------------
        bot.send_msg('Running cdr analysis...')
        CDRAnalysis(
            params=nest.params,
            data_feature_extracted=cdr_data.data_feature_extracted
        )

if __name__ == "__main__":
    pipeline()

