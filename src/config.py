import os
import geocoder
from datetime import datetime
from collections import namedtuple

_curr_dir = os.path.dirname(os.path.realpath(__file__))
_export_dir = os.path.join(_curr_dir, 'output/')
_constants = {
    'SQL_DIR': os.path.join(_curr_dir, 'sql'),
    'LOG_DIR': os.path.join(_curr_dir, 'logs'),
    'OUTPUT_DIR': os.path.join(_curr_dir, 'output'),
    'PARAMS_FILE': os.path.join(_curr_dir, 'params.yaml'),
    'export_to_csv': True,
    'user_time': str(datetime.now()),
    'user_location': (geocoder.ip('me')).latlng,

    # museum data paths
    'museum_raw': os.path.join(_export_dir, '_museumdata_raw.csv'),
    'museum_feature_extracted': os.path.join(_export_dir, '_museumdata_feature_extracted.csv'),

    # cdr data paths
    'cdr_raw': os.path.join(_export_dir, 'cdr_raw_data.csv'),
    'cdr_feature_extracted': os.path.join(_export_dir, 'cdr_feature_extracted.csv'),

    # visualization paths
    'museum_fountain': os.path.join(_export_dir, 'museum_fountain.json'),
    'tower_routes_pickle': os.path.join(_export_dir, 'tower_routes.pickle'),
    'tower_routes_json': os.path.join(_export_dir, 'tower_routes.json'),
    'museum_routes': os.path.join(_export_dir, 'museum_routes.pickle'),
    'routes': os.path.join(_export_dir, 'routes.pickle'),
    'location_dict_path': os.path.join(_export_dir, 'museum_dict.json'),
    'geojson_path': os.path.join(_export_dir, 'output', 'florence_voronoi_with_area.geojson')
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
