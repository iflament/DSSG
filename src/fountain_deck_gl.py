import json
from config import constants


class FountainViz:
    """ Takes Pandas formatted data and creates JSON data files formatted to be consumed
    by the fountain visualization made with Deck.GL """

    def __init__(self, network_analysis, museum_data):
        self.network_analysis = network_analysis
        self.museum_data = museum_data
        self.museum_viz(constants.location_dict_path)

    def museum_viz(self):
        """  Main function for producing the appropriate JSON files to feed into the Firenze card museum
        fountain visualization made with Deck.GL"""

        records = self.museum_data.locations_data[['museum_id', 'latitude', 'longitude', 'short_name', 'museum_name']]
        records = records[records.museum_id < self.params.fountain_museum_maxid]

        network_df = self.museum_data.data_featured_extracted[['museum_id', 'date', 'user_id']]
        network_df['total_people'] = 1

        dynamic_edges = self.network_analysis._get_dynamic_edgelist(network_df, location='museum_id')

        edges = self.network_analysis._get_static_edgelist(dynamic_edges)
        geojson, location_dict = self.create_geojson(records, edges)

        with open(constants.fountain_json_path, 'w') as outfile:
            json.dump(geojson, outfile, indent=2)

        with open(constants.location_dict_path, 'w') as outfile:
            json.dump(location_dict, outfile, indent=2)

    def create_geojson(self, nodes, edges, geometries, fountain_type):
        """ Create a geojson file that is formatted to be consumed by the Deck.GL
        fountain visualization. Makes a dictionary of all of the names and printable
        names of the locations in a separate file.

        :param nodes (list) The list of nodes that will be used for the visualization. Each node in the list is a
        tuple of (id, lat, lon, name, full_name)
        :param edges (Pandas.DataFrame) The weight for each edge to and from a pair of nodes contained in the
        node list. Should contain a column for to, from, and weight of that edge. Optional args for those column names.
        :param geometries (dict) polygon geometry and area for each unique region id
        :param fountain_type (int) Type of fountain to create feature for

        :return tuple (dict, dict) the geojson object containing all of the feature definitions and the object
        containing all the location names by id """

        location_dict = {
            'source': {
                'name': 'Unknown',
                'fullName': 'Unknown'
            },
            'start': {
                'name': 'Start',
                'fullName': 'Start'

            },
            'end': {
                'name': 'End',
                'fullName': 'End'

            }
        }

        group_perc = self.create_percentage_column(edges, 'perc_to', columns=["to", "from", "weight"])
        updated_edges = self.create_percentage_column(group_perc, 'perc_from',
                                                      columns=["from", "to", "weight", 'perc_to'])

        features = [self.create_feature(f, updated_edges, location_dict, geometries=geometries,
                                        fountain_type=fountain_type) for f in nodes]

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        return geojson, location_dict

    @staticmethod
    def create_percentage_column(df, perc_col_name, columns):
        """ Takes a dataframe with a weight column and calculates what percentage each
        weight is of the total sum of all of the weights.

        :param df dataframe to add a percentage column to
        :param perc_col_name (string) name to give to the new percentage column
        :param columns to group by """

        df[perc_col_name] = df["weight"]
        group_sum = df.groupby(columns).agg({perc_col_name: 'sum'})

        group_perc = group_sum.groupby(level=0) \
            .apply(lambda x: 100 * x / float(x.sum()))

        return group_perc.reset_index()

    def create_feature(self, datum, edges, location_dict, geometries, fountain_type):
        """ Create a feature geojson object for the specified node in the fountain

        :param datum (list) one fountain node with an node_id, latitude, longitude, name, and printable name.
        :param edges (Pandas.DataFrame) The weight for each edge to and from a pair of nodes contained in the node
        list. Should contain a column for to, from, and weight of that edge. Optional args for those column names.
        :param location_dict (dict) dictionary of all of the names and printable names for every location by node_id.
        :param geometries (dict) polygon geometry and area for each unique node_id
        :param fountain_type (int) Type of fountain to create feature for

        :return (dict) a geojson feature definition object for the supplied datum """

        node_id, lat, lon, name, full_name = datum
        lat = float(lat)
        lon = float(lon)
        node_id = str(node_id)

        edges["to"] = edges["to"].apply(
            lambda row: str(int(row)) if isinstance(row, float) else str(row))
        edges["from"] = edges["from"].apply(
            lambda row: str(int(row)) if isinstance(row, float) else str(row))

        edges = edges.loc[(edges["to"] == node_id) | (edges["from"] == node_id)]

        start_props = None
        if geometries is not None and node_id in geometries:
            geometry = geometries[node_id]['geometry']
        else:
            geometry = self.create_geometry(lat, lon)

        if fountain_type is self.params.fountain_type_MUSEUM:
            total_museum_visits = edges[(edges["to"] == node_id)].sum()
            total_museum_visits = str(int(total_museum_visits["weight"]))
            start_props = {'totalMuseumVisits': total_museum_visits}

        feature = {
            'type': 'Feature',
            'geometry': geometry,
            'properties': self.create_properties(node_id, name, full_name, [lon, lat],
                                                 edges, location_dict, start_props)
        }

        return feature

    def create_properties(self, node_id, name, full_name, centroid, edges, location_dict, props):
        """ Create the additional properties object for the geojson. This contains the id, name, printable name,
        centroid lat/lon, edges in and out, density in the node, area of the node, total visits to the node, and total
        museum visits to the node. Some of the properties are null for the non applicable value.

        :param node_id (string) the unique id for the node
        :param name (string) the shorthand name of the node
        :param full_name the long version of the name of the node
        :param centroid (list) the center lat/lon of the node
        :param edges (Pandas.DataFrame) The weight for each edge to and from a pair of nodes contained in the node
        list. Should contain a column for to, from, and weight of that edge.
        :param location_dict (dict) dictionary of all of the names and printable names for every location by id.
        :param props (dict) the optional starting properties for each unique id node

        :return (dict) the newly created properties object for the geojson feature """

        in_flows, out_flows = self.create_flows(edges, node_id)

        if props is None:
            props = {}

        props.update({
            'name': name,
            'fullName': full_name,
            'id': str(node_id),
            'inFlows': in_flows,
            'outFlows': out_flows,
            'centroid': centroid
        })

        location_dict[str(node_id)] = {
            'name': name,
            'fullName': full_name,
        }

        return props

    @staticmethod
    def create_flows(edges, node_id):
        """ Create the geojson property object that enumerates the flow volume to and
        from a location for the fountain.

        :param edges (dataframe) The weight for each edge to and from a pair of nodes contained
        in the node list. Should contain a column for to, from, and weight of that edge.
        Optional args for those column names.
        :param node_id (string) identifier of node for which to map in and out flows

        :return tuple (dict, dict): the objects for the flows in and out of the node to each
        other node in the fountain for which there is a directed edge """

        in_flows = {}
        out_flows = {}
        in_edges = edges.loc[(edges["to"] == node_id)]
        out_edges = edges.loc[(edges["from"] == node_id)]

        for index, edge in in_edges.iterrows():
            from_id = edge["from"]
            if isinstance(from_id, float):
                from_id = int(from_id)

            in_flows[from_id] = {
                'weight': edge["weight"],
                'percentage': edge['perc_to']
            }

        for index, edge in out_edges.iterrows():
            to_id = edge["to"]
            if isinstance(to_id, float):
                to_id = int(to_id)

            out_flows[to_id] = {
                'weight': edge["weight"],
                'percentage': edge['perc_from']
            }

        return in_flows, out_flows

    @staticmethod
    def format_museum_properties(museums):
        """ Converts the format of additional museum properties from being in a DataFrame to being in a dictionary
        indexed by the museum node id

        :param museums (dataframe) museum id and corresponding number of visitors at that museum node
        :return (dict) object with a key for each museum node id and a value that is an object with value for
        number of state and national museum visitors, aka total visitors, to that museum. """

        props = {}
        ids = museums["museum_id"].unique()

        for museum_id in ids:
            museum_id = str(int(museum_id))
            museums["museum_id"] = museums["museum_id"].apply(str)
            first_match = museums[museums["museum_id"] == museum_id].head(1)

            total_visits = None
            if not first_match.empty:
                total_visits = first_match["visitors"].iloc[0]

            props[str(museum_id)] = {'totalVisits': total_visits}

        return props




