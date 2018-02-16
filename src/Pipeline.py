import logging
from config import constants, logger_config
from data import DataHandler
from preprocess import MuseumDataPreProcess, CDRPreProcess
from museum import SiteAnalysis
from telecom import CDRAnalysis
from network_analysis import NetworkAnalysis
from fountain_deck_gl import FountainViz
from bot import SlackBot
import click

logger = logging.getLogger(__name__)

@click.command()
@click.option('--city', type=str, default='Florence')
@click.option('--slackbot', is_flag=True, default=True)
@click.option('--export', is_flag=True, default=True)
@click.option('--sitedata', is_flag=True, default=True)
@click.option('--sitedata_format', type=str, default="local_file")
@click.option('--cdrdata', is_flag=True, default=True)
@click.option('--cdrdata_format', type=str, default="local_file")
@click.option('--net_analysis', is_flag=True, default=True)
@click.option('--vis', is_flag=True, default=False)
@click.option('--sampling', is_flag=True, default=False)
@click.option('--sample_size', type=int, default=1000)
def pipeline(city, slackbot, export, sitedata, sitedata_format,
             cdrdata, cdrdata_format, net_analysis, vis,
             sampling, sample_size):

    logging.config.dictConfig(logger_config)

    # ---------------------------------------
    # Get Params and Constants, Load data
    # ---------------------------------------
    nest = DataHandler(city, slackbot, export, sitedata,
                       sitedata_format, cdrdata, cdrdata_format,
                       net_analysis, vis, sampling, sample_size)

    if nest.click_params.sitedata:
        # -----------------------
        # Preprocess Museum data
        # -----------------------
        site_data = MuseumDataPreProcess(
            click_params=nest.click_params,
            params=nest.params,
            site_raw_data=nest.site_raw_data
        )

        # ---------------------------------------
        # Site Data Analysis
        # ---------------------------------------
        SiteAnalysis(
            click_params=nest.click_params,
            params=nest.params,
            data_feature_extracted=site_data.data_feature_extracted
        )

    if nest.click_params.net_analysis:
        # ---------------------------------------
        # Network Analysis
        # ---------------------------------------
        network_analysis = NetworkAnalysis(
            params=nest.params,
            data=site_data.data_feature_extracted
        )

    if nest.click_params.vis:
        # --------------------------------------------
        # Create Fountain Visualization of museum data
        # --------------------------------------------
        FountainViz(
            network_analysis=network_analysis,
            museum_data=site_data
        )

    if nest.click_params.cdrdata:
        # --------------------
        # Preprocess Cdr data
        # --------------------
        cdr_data = CDRPreProcess(
            click_params=nest.click_params,
            params=nest.params,
            cdr_raw_data=nest.cdr_raw_data
        )

        # ---------------------------------------
        # CDR Data Analysis
        # ---------------------------------------
        CDRAnalysis(
            params=nest.params,
            data_feature_extracted=cdr_data.data_feature_extracted
        )

        if slackbot:
            SlackBot(nest, network_analysis, channel='city-flows-bot')

if __name__ == "__main__":
    pipeline()
