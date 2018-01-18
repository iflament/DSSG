import logging
from config import constants, logger_config
from data import DataHandler
from preprocess import MuseumDataPreProcess, CDRPreProcess
from museum import MuseumAnalysis
from telecom import CDRAnalysis
from network_analysis import NetworkAnalysis
import pandas as pd
from pandas_schema import Column, Schema
from pandas_schema.validation import IsDtypeValidation, DateFormatValidation

logger = logging.getLogger(__name__)


def pipeline():

    logging.config.dictConfig(logger_config)

    # ---------------------------------------
    # Get Params and Constants
    # ---------------------------------------
    nest = DataHandler()
    params_file = constants.PARAMS_FILE
    params = nest._load_params()

    # ---------------------------------------
    # Load data #todo load directly from S3 bucket or DB
    # ---------------------------------------
    museum_raw_data = pd.read_csv(constants.museum_raw)
    museum_locations_data = pd.read_csv(constants.museum_locations)
    cdr_raw_data = pd.read_csv(constants.cdr_raw)

    # ---------------------------------------
    # Data validation #todo: dump this into data module in a validation class
    # ---------------------------------------
    cdr_schema = Schema([
        Column('user_id', [IsDtypeValidation(int)]),
        Column('latitude', [IsDtypeValidation(float)]),
        Column('longitude', [IsDtypeValidation(float)]),
        Column('user_origin', [IsDtypeValidation(str)]),
        Column('in_city_boundaries', [IsDtypeValidation(str)]),
        Column('date_time', [IsDtypeValidation(str), DateFormatValidation(str)]),
        Column('tower_id', [IsDtypeValidation(int)])
    ])

    errors = cdr_schema.validate(cdr_raw_data)
    logger.info(errors)

    for error in errors:
        print(error)

    # ---------------------------------------
    # Preprocessing & Feature Extraction
    # ---------------------------------------
    museum_data = MuseumDataPreProcess(
        params=params,
        museum_raw_data=museum_raw_data,
        museum_locations_data=museum_locations_data
    )

    cdr_data = CDRPreProcess(
        params=params,
        cdr_raw_data=cdr_raw_data
    )

    # Run Situation Analyses on Museum and CDR data...
    # ---------------------------------------
    # Museum Data Analysis
    # ---------------------------------------
    MuseumAnalysis(
        params=params,
        data_feature_extracted=museum_data.data_feature_extracted
    )

    # ---------------------------------------
    # CDR Data Analysis
    # ---------------------------------------
    CDRAnalysis(
        params=params,
        cdr_raw_data=cdr_data.data_feature_extracted
    )

    # ---------------------------------------
    # Museum Network Analysis
    # ---------------------------------------
    NetworkAnalysis(
        params=params,
        data=museum_data.data_feature_extracted
    )


if __name__ == "__main__":
    pipeline()

