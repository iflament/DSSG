import os
import geocoder
from datetime import datetime
from collections import namedtuple

_curr_dir = os.path.dirname(os.path.realpath(__file__))
_export_dir = os.path.join(_curr_dir, 'output/')
_constants = {
    'SQL_DIR': os.path.join(_curr_dir, 'sql'),
    'LOG_DIR': os.path.join(_curr_dir, 'logs'),
    'SITES_DIR': os.path.join(_curr_dir, 'sites_data'),
    'PARAMS_FILE': os.path.join(_curr_dir, 'params.yaml'),
    'connect_to_db': False,
    'export_to_csv': True,
    'user_time': str(datetime.now()),
    'user_location': (geocoder.ip('me')).latlng,

    # museum data paths
    'national_museums_data': os.path.join(_export_dir, '_nationalmuseums_raw.csv'),
    'firenzelocations_data': os.path.join(_export_dir, '_firenzedata_locations.csv'),
    'firenzedata_feature_extracted': os.path.join(_export_dir, '_firenzedata_feature_extracted.csv'),
    'firenzedata_raw': os.path.join(_export_dir, '_firenzedata_raw.csv'),
    'museum_list': ['Santa Croce', 'Opera del Duomo', 'Uffizi', 'Accademia',
                    'M. Casa Dante', 'M. Palazzo Vecchio', 'M. Galileo', 'M. Bargello',
                    'San Lorenzo', 'M. Archeologico', 'Pitti', 'Cappelle Medicee',
                    'M. Santa Maria Novella', 'M. San Marco', 'Laurenziana',
                    'M. Innocenti', 'Palazzo Strozzi', 'Palazzo Medici',
                    'Torre di Palazzo Vecchio', 'Brancacci', 'M. Opificio',
                    'La Specola', 'Orto Botanico', 'V. Bardini', 'M. Stefano Bardini',
                    'M. Antropologia', 'M. Ebraico', 'M. Marini', 'Casa Buonarroti',
                    'M. Horne', 'M. Ferragamo', 'M. Novecento', 'M. Palazzo Davanzati',
                    'M. Geologia', 'M. Civici Fiesole', 'M. Stibbert', 'M. Mineralogia',
                    'M. Preistoria', 'M. Calcio', 'Primo Conti','All Museums'],

    # cdr data paths
    'cdr_daytrippers': os.path.join(_export_dir, 'cdr_daytripper_fountain.json'),
    'cdr_daytrippers_dict': os.path.join(_export_dir, 'cdr_daytripper_dict.json'),
    'cdr_towers': os.path.join(_export_dir, 'cdr_labeled_tower.csv'),
    'cdr_foreigners_raw': os.path.join(_export_dir, 'cdr_foreigners.csv'),
    'cdr_italians_raw': os.path.join(_export_dir, 'cdr_italians.csv'),
    'cdr_feature_extracted': os.path.join(_export_dir, 'cdr_feature_extracted.csv'),

    # visualization paths
    'museum_fountain': os.path.join(_export_dir, 'museum_fountain.json'),
    'tower_routes_pickle': os.path.join(_export_dir, 'tower_routes.pickle'),
    'tower_routes_json': os.path.join(_export_dir, 'tower_routes.json'),
    'museum_routes': os.path.join(_export_dir, 'museum_routes.pickle'),
    'routes': os.path.join(_export_dir, 'routes.pickle'),  # routes_path (string): The file path for the routes pickle

    # network analysis paths
    'foreign_daytrippers_edges': os.path.join(_export_dir, 'foreign_daytripper_edges.pickle'),  # edges_pickle (string): file path for pickle object with edges
    'density_pickle': os.path.join(_export_dir, 'foreign_daytripper_region_density.pickle'),  # density_pickle (string): file path for pickle object with node densities
    'geojson_path': os.path.join(_export_dir, 'florence_voronoi_with_area.geojson'),  # geojson_path (string): file path for tower voronoi geojson definitions
    'end_node_csv': os.path.join(_export_dir, 'daytripper_end_nodes.csv'),  # end_nodes_path (string): file path for output csv of most common end nodes in ranked order
    'start_node_csv': os.path.join(_export_dir,  'daytripper_start_nodes.csv')  # start_nodes_path (string): file path for output csv of most common start nodes in ranked order

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
