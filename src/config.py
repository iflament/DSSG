import os
import utils
from collections import namedtuple

_curr_dir = os.path.dirname(os.path.realpath(__file__))
_data_dir = os.path.join(_curr_dir, 'data/')
_credentials = utils.read_yaml(os.path.join(_curr_dir, 'credentials.yaml'))
_constants = {
    'SQL_DIR': os.path.join(_curr_dir, 'sql_templates'),
    'LOG_DIR': os.path.join(_curr_dir, 'logs'),
    'ANALYSIS_PARAMS_FILE': os.path.join(_curr_dir, 'params.yaml'),

    # museum data paths
    'site_input_data': os.path.join(_data_dir, 'museumdata_CF.csv'),  # the path to raw data
    'site_output_data': os.path.join(_data_dir, '_museumdata_feature_extracted.csv'),  # output path of feature extracted data

    # list of museum names
    'site_list': ['Santa Croce', 'Opera del Duomo', 'Uffizi', 'Accademia', 'M. Casa Dante', 'M. Palazzo Vecchio',
                    'M. Galileo', 'M. Bargello', 'San Lorenzo', 'M. Archeologico', 'Pitti', 'Cappelle Medicee',
                    'M. Santa Maria Novella', 'M. San Marco', 'Laurenziana', 'M. Innocenti', 'Palazzo Strozzi',
                    'Palazzo Medici', 'Torre di Palazzo Vecchio', 'Brancacci', 'M. Opificio', 'La Specola',
                    'Orto Botanico', 'V. Bardini', 'M. Stefano Bardini', 'M. Antropologia', 'M. Ebraico',
                    'M. Marini', 'Casa Buonarroti', 'M. Horne', 'M. Ferragamo', 'M. Novecento',
                    'M. Palazzo Davanzati', 'M. Geologia', 'M. Civici Fiesole', 'M. Stibbert', 'M. Mineralogia',
                    'M. Preistoria', 'M. Calcio', 'Primo Conti'],

    # cdr data paths
    'cdr_input_data': os.path.join(_data_dir, 'cdrdata_CF.csv'),  # the path to raw data
    'cdr_output_data': os.path.join(_data_dir, 'cdr_feature_extracted.csv'),  # output path of feature extracted data

    # visualization paths
    'museum_fountain': os.path.join(_data_dir, 'museum_fountain.json'),
    'tower_routes_pickle': os.path.join(_data_dir, 'tower_routes.pickle'),
    'tower_routes_json': os.path.join(_data_dir, 'tower_routes.json'),
    'museum_routes': os.path.join(_data_dir, 'museum_routes.pickle'),
    'routes': os.path.join(_data_dir, 'routes.pickle'),
    'location_dict_path': os.path.join(_data_dir, 'museum_dict.json'),
    'geojson_path': os.path.join(_data_dir, 'output', 'florence_voronoi_with_area.geojson')
}

constants = (namedtuple('Constants', _constants)(**_constants))

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s-%(name)s-%(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'filename': os.path.join(constants.LOG_DIR, 'logs.log'),
            'maxBytes': 20971520,  # 20 Mb
            'backupCount': 9,
            'encoding': 'utf8'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
