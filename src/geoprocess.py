import pandas as pd
import shapely as sp
import numpy as np
import math
import geopandas as gpd
from scipy.spatial import Voronoi
from config import constants, logger_config, _export_dir
import logging
import logging.config

logger = logging.getLogger(__name__)


class GeoProcess:
    """ Prepare data objects for geo analysis """

    logging.config.dictConfig(logger_config)

    @staticmethod
    def convert_point_csv_to_data_frame(path):
        """ Takes a CSV file with latitude and longitude columns and returns a Geopandas
        DataFrame object. This function accepts optional configuration params for
        the CSV
        :param: path (string): file path for the CSV file
        :return: GeoPandas.GeoDataFrame: the contents of the supplied CSV file in the
        format of a GeoPandas GeoDataFrame
        """

        csv_points = pd.read_csv(path, encoding='utf-8', sep='\t',
                                 index_col=None, decimal='.')

        zipped_data = zip(csv_points['lon'], csv_points['lat'])
        geo_points = [sp.geometry.Point(xy) for xy in zipped_data]
        crs = {'init': 'epsg:' + str(4326)}
        geo_df = gpd.GeoDataFrame(csv_points, crs=crs, geometry=geo_points) \
            .to_crs(epsg=4326)

        return geo_df

    @staticmethod
    def convert_point_data_to_data_frame(data):
        """ Takes a data set with latitude and longitude columns and returns a Geopandas
        GeoDataFrame object.
        :param: data (Pandas.DataFrame): the lat/lon data to convert to GeoDataFrame
        :return: GeoPandas.GeoDataFrame: the contents of the supplied data in the
        format of a GeoPandas GeoDataFrame
        """

        zipped_data = zip(data['lon'], data['lat'])
        geo_points = [sp.geometry.Point(xy) for xy in zipped_data]
        crs = {'init': 'epsg:' + str(4326)}

        return gpd.GeoDataFrame(data, crs=crs, geometry=geo_points) \
            .to_crs(epsg=4326)

    @staticmethod
    def get_points_inside_shape(points, shape):
        """ Takes a point geometry object and a polygon geometry shape file
        and returns all of the points within the boundaries of that shape
        :param: points (Geopandas.GeoDataFrame): Point geometry
        :param: shape (Geopandas.GeoDataFrame): Polygon geometry shape file object
        :return: Geopandas.GeoDataFrame: points that are within the outline of the shape
        """

        return points[points.within(shape.unary_union)]

    @staticmethod
    def create_voronoi(points):
        """ Make a voronoi diagram geometry out of point definitions
        :param: points (Geopandas.GeoDataFrame): The centroid points for the voronoi
        :return: Geopandas.GeoDataFrame: The polygon geometry for the voronoi diagram
        """

        np_points = [np.array([pt.x, pt.y]) for pt in np.array(points.geometry)]
        vor = Voronoi(np_points)

        lines = [
            sp.geometry.LineString(vor.vertices[line])
            for line in vor.ridge_vertices
            if -1 not in line
        ]

        voronoi_poly = sp.ops.polygonize(lines)
        crs = {'init': 'epsg:' + str(4326)}
        return gpd.GeoDataFrame(crs=crs, geometry=list(voronoi_poly)) \
            .to_crs(epsg=4326)

    def make_voronoi_in_shp(self, points, shape):
        """ Make a voronoi diagram geometry out of point definitions and embed it in a
        shape.
        :param: points (Geopandas.GeoDataFrame): The centroid points for the voronoi
        :param: shape (Geopandas.GeoDataFrame): The shapefile to contain the voronoi inside
        :return: Geopandas.GeoDataFrame: The polygon geometry for the voronoi diagram
        embedded inside the shape
        """

        # epsg (int): spatial reference system code for geospatial data
        voronoi_geo = self.create_voronoi(points)
        voronoi_geo_in_shape = self.get_points_inside_shape(voronoi_geo, shape)

        shape_with_voronoi = gpd.sjoin(points, voronoi_geo_in_shape, how="inner",
                                       op='within')

        del shape_with_voronoi['geometry']

        return voronoi_geo_in_shape.merge(shape_with_voronoi, left_index=True,
                                          right_on='index_right')

    @staticmethod
    def process_geometries_geojson(geometries):
        """
        :param: geometries (dict): The loaded geometries json object
        :return: new object containing geojson geometries original object now
        formatted as dict where keys are the feature id and value is object with the geometry and
        area.
        """

        geo_dict = {}

        for feature in geometries['features']:
            geo_dict[str(feature['properties']['id'])] = {
                'geometry': feature['geometry'],
                'area': feature['properties']['area']
            }

        return geo_dict

    def create_geometry(self, lat, lon):
        """ Create a geojson Polygon geometry object with a circular Polygon that has
        a centroid at the specified latitude and longitude.
        :param: lat (float): the latitude for the center of the circle
        :param: lon (float: the longitude for the center of the circle
        :return: dict: the newly created Polygon geojson object
        """

        geometry = {
            'type': 'Polygon',
            'coordinates': [self.create_circle(lat, lon)]
        }

        return geometry

    @staticmethod
    def create_circle(lat, lon, radius=18, num_points=20):
        """ Create the approximation or a geojson circle polygon
        :param: lat: the center latitude for the polygon
        :param: lon: the center longitude for the polygon
        :param: radius (int): the radius of the circle polygon
        :param: num_points (int): number of discrete sample points to be generated along the circle
        :return: list of lat/lon points defining a somewhat circular polygon
        """

        points = []
        for k in range(num_points):

            angle = math.pi * 2 * k / num_points
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)

            new_lat = lat + (180 / math.pi) * (dy / 6378137)
            new_lon = lon + (180 / math.pi) * (dx / 6378137) / math.cos(
                lat * math.pi / 180)

            points.append([round(new_lon, 7), round(new_lat, 7)])

        return points

    @staticmethod
    def create_square(lat, lon, radius=0.0001):
        """ Create the a geojson square polygon
        :param: lat: the center latitude for the polygon
        :param: lon: the center longitude for the polygon
        :param: radius (int): half of the length of the edge of the square
        :return: list of lat/lon points defining a square polygon
        """

        return [
            [round(lon + radius, 7), round(lat + radius, 7)],
            [round(lon + radius, 7), round(lat - radius, 7)],
            [round(lon - radius, 7), round(lat - radius, 7)],
            [round(lon - radius, 7), round(lat + radius, 7)]
        ]


