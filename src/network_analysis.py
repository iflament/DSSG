
import matplotlib.ticker as ticker
from pylab import *
import igraph as ig
import pandas as pd
import numpy as np
from config import constants, logger_config, _data_dir
import logging.config
import logging
import credentials
import plotly

plotly.tools.set_credentials_file(username=credentials.plotlyu, api_key=credentials.plotlykey)
logger = logging.getLogger(__name__)


class NetworkAnalysis:

    """ Network Analysis """

    logging.config.dictConfig(logger_config)

    def __init__(self, params, data):
        self.params = params
        self.data = data
        self.dynamic_edgelist = self._get_dynamic_edgelist(self.data)
        self.static_edgelist = self._get_static_edgelist(self.dynamic_edgelist)
        graph = self._get_static_graph()
        graph = self._delete_paired_edges(graph)
        self._plot_static_graph(graph)
        self.transition_matrix = self._get_origin_destination_matrix(graph)
        self._plot_origin_destination_matrix_heatmap()
        self.fountain_edges = self._get_fountain_edgelist()
        # TODO: fix aggregated paths
        # self.aggregated_paths = self._aggregate_daily_paths()
        self.paths = self._get_daily_paths()
        # self._plot_aggregate_daily_paths()

    def _get_fountain_edgelist(self):
        """ Get edgelist for fountain vizualisation (helper function)"""
        df = self.data[self.data['museum_id'] < 43]
        df['total_people'] = 1
        dynamic_edges = self._get_dynamic_edgelist(df)
        fountain_edges = self._get_static_edgelist(dynamic_edges)

        return fountain_edges

    @staticmethod
    def _get_dynamic_edgelist(data):
        """ Make an edge list for all of the sequential visits of one site to the next
        in a day per user. Each edge is directed. There is a dummy start node to
        indicate the transition from being home to the first site visited that day """

        edges = data.groupby(["user_id", "entry_time", "date",
                              "short_name"]).sum()["total_people"].to_frame()
        edges.reset_index(inplace=True)

        # start is the name of the dummy node for edges from home to the first location visited
        edges["from"] = 'dummy_start_node'
        edges["to"] = edges["short_name"]

        make_link = (edges["user_id"].shift(1) == edges["user_id"]) & \
                    (edges["date"].shift(1) == edges["date"])

        edges["from"][make_link] = edges["short_name"].shift(1)[make_link]
        dynamic_edgelist = edges[["from", "to", "total_people", "entry_time"]]

        return dynamic_edgelist

    def _get_static_edgelist(self, dynamic_edgelist):
        """ Create a static edge list for the firenze card entry logs from the dynamic
        edge list.
        :param (Pandas.DataFrame): dynamic edgelist created by make_dynamic_firenze_card_edgelist. """

        # TODO: Need to create an "end" of day node
        supp = dynamic_edgelist[dynamic_edgelist[self.params.net_source].shift(-1) == 'start'][[
            self.params.net_target, self.params.net_count]]
        supp.columns = [self.params.net_source, self.params.net_count]
        supp[self.params.net_target] = 'end'
        supp = supp[[self.params.net_source, self.params.net_target, self.params.net_count]]
        supp_edges = supp.groupby([self.params.net_source, self.params.net_target])[self.params.net_count].sum().\
            to_frame().reset_index()
        static_edgelist = pd.concat([dynamic_edgelist.groupby([self.params.net_source, self.params.net_target])
                            [self.params.net_count].sum().to_frame().reset_index(), supp_edges])
        static_edgelist.columns = ['from', 'to', 'weight']

        return static_edgelist

    def _get_static_graph(self):
        """ Create an iGraph network graph from the static edge list created from the
        firenze card entry logs. """

        df_nodes = self.data[['latitude', 'longitude', 'short_name']]
        g = ig.Graph.TupleList(self.static_edgelist.itertuples(index=False), directed=True, weights=True)

        g.vs['indeg'] = g.strength(mode='in', weights='weight')
        g.vs['outdeg'] = g.strength(mode='out', weights='weight')

        # are there any null weights?
        # logger.info(g.es["weight"] == 0)

        # vertice degrees that are null?
        # logger.info(g.vs["indeg"] == 0)
        # logger.info(g.vs["outdeg"] == 0)

        # Get rid of the few self-loops, which can plot strangely
        g.simplify(loops=False, combine_edges=sum)

        g.vs['label'] = g.vs["name"]
        # Put in graph attributes to help with plotting
        g.vs['size'] = [.00075 * i for i in g.strength(mode='in', weights='weight')]  # .00075 is from hand-tuning

        # Get coordinates, requires this lengthy query
        location = pd.DataFrame({self.params.net_join_column: g.vs['label']}).merge(
            df_nodes[[self.params.net_join_column, self.params.net_lon, self.params.net_lat]],
            left_index=True, how='left', on=self.params.net_join_column
        )
        # logger.info(location)
        g.vs['x'] = (location[self.params.net_lon]).values.tolist()

        # Latitude is flipped, need to multiply by -1 to get correct orientation
        g.vs['y'] = (-1 * location[self.params.net_lat].values).tolist()

        return g

    def _delete_paired_edges(self, graph):
        """ Delete both directions of edge between a source and target location. This mutates the graph object
        supplied to this function.
        :param graph (igraph.Graph): the graph to remove the edges from """

        graph.delete_edges(graph.es.find(_between=(graph.vs(name_eq=self.params.net_site_source),
                                                   graph.vs(name_eq=self.params.net_site_target))))

        graph.delete_edges(graph.es.find(_between=(graph.vs(name_eq=self.params.net_site_target),
                                                   graph.vs(name_eq=self.params.net_site_source))))

        # logger.info(graph.degree(type='in'))
        # logger.info(graph.degree(type='out'))
        # logger.info(min(graph.edge_betweenness()))

        return graph

    @staticmethod
    def _plot_static_graph(graph):
        """ Plot the igraph network graph for the firenze card locations network """

        visual_style = {}
        outdegree = graph.outdegree()
        visual_style["vertex_size"] = [x / max(outdegree) * 25 + 50 for x in outdegree]

        # Set bbox and margin
        visual_style["bbox"] = (800, 800)
        visual_style["margin"] = 100

        # Define colors used for outdegree visualization
        colours = ['#fecc5c', '#a31a1c']

        # Order vertices in bins based on outdegree
        bins = np.linspace(0, max(outdegree), len(colours))
        digitized_degrees = np.digitize(outdegree, bins)

        # Set colors according to bins
        graph.vs["color"] = [colours[x - 1] for x in digitized_degrees]

        # Also color the edges
        for ind, color in enumerate(graph.vs["color"]):
            edges = graph.es.select(_source=ind)
            edges["color"] = [color]

        # Don't curve the edges
        visual_style["edge_curved"] = False

        # Choose the layout
        N = len(graph.vs)
        visual_style["layout"] = graph.layout_fruchterman_reingold(
            weights=graph.es["weight"],
            maxiter=10,
            area=N ** 3,
            repulserad=N ** 3
        )

        # Plot the graph
        # TODO fix error: Illegal format string "graph.pdf"; two color symbols
        # plot(graph, 'graph.pdf', **visual_style)

    @staticmethod
    def _get_origin_destination_matrix(graph):
        """ Create a transition matrix for all possible transitions between pairs of
        sites from the igraph network graph.

        :param graph (igraph.Graph): the graph object for a weighted, directed graph """

        transition_matrix = pd.DataFrame(
            graph.get_adjacency(
                attribute='weight').data,
            columns=graph.vs['name'],
            index=graph.vs['name']
        )

        order = transition_matrix.sum(1).sort_values(ascending=False).to_frame().index

        return transition_matrix[order].reindex(order)

    def _plot_origin_destination_matrix_heatmap(self):
        """ Plot the heat map for the transition matrix created from the network graph """

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)

        cmap = plt.cm.PuBu
        cax = ax.matshow(np.log(self.transition_matrix), cmap=cmap)
        fig.colorbar(cax)

        ax.set_xticklabels([''] + self.transition_matrix.index.tolist(), rotation=90)
        ax.set_yticklabels([''] + self.transition_matrix.index.tolist())

        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

        savefig('network_transition_matrix.png')

        return

    def _get_daily_paths(self):
        """ Creates a DataFrame that has paths, which are a string of single-character
        codes concatenated, for a user per day from the Firenze card logs. """

        temp = self.data.groupby(['user_id', 'entry_time', 'date', 'string']).sum()['total_people'].to_frame()
        temp.reset_index(inplace=True)

        temp['start'] = ' '
        temp['target'] = temp['string']

        make_link = (temp['user_id'].shift(1) == temp['user_id']) & \
                    (temp['date'].shift(1) == temp['date'])

        temp['start'][make_link] = temp['string'].shift(1)[make_link]
        temp['start'][temp['start'].shift(-1) == ' '] = \
            (temp['start'] + temp['target'])[temp['start'].shift(-1) == ' ']

        temp.iloc[-1:]['start'] = temp.iloc[-1:]['start'] + temp.iloc[-1:]['target']

        paths = temp.groupby('user_id')['start'].sum().to_frame()

        return paths['start'].apply(lambda x: pd.Series(x.strip().split(' ')))

    @staticmethod
    def _frequency(data, column_name):
        """ Creates a frequency table from a dataframe column that is suitable for
        plotting the empirical PMF, empirical CDF, or empirical CCDF. """

        out = data[column_name].value_counts().to_frame()
        out.columns = ['frequency']
        out.index.name = column_name
        out.reset_index(inplace=True)
        out.sort_values('frequency', inplace=True, ascending=False)

        out['cumulative'] = out['frequency'].cumsum() / out['frequency'].sum()
        out['ccdf'] = 1 - out['cumulative']

        return out

    def _aggregate_daily_paths(self):
        """ Creates a dataframe with daily paths per user aggregated across all users
        and all days. """

        pt = pd.concat([self._frequency(self.data, 0), self._frequency(self.data, 1), self._frequency(self.data, 2),
                        self._frequency(self.data, 3)])

        pt['daily_path'] = pt[0].replace(np.nan, '', regex=True) + \
                           pt[1].replace(np.nan, '', regex=True) + \
                           pt[2].replace(np.nan, '', regex=True) + \
                           pt[3].replace(np.nan, '', regex=True)

        pt.drop([0, 1, 2, 3, 'ccdf', 'cumulative'], axis=1, inplace=True)

        pt_grouped = pt.groupby('daily_path').sum()
        pt_grouped.sort_values('frequency', inplace=True, ascending=False)

        return pt_grouped

    def _plot_aggregate_daily_paths(self):
        """ Plot the frequency of each daily path aggregated across all days and users """

        self.data[self.data['frequency'] > 200].plot.bar(figsize=(16, 8))
        plt.title('Most common daily Firenze card paths across all days')
        plt.xlabel('x = Encoded path')
        plt.ylabel('Number of cards with daily path x')

        if self.params.net_use_log_scale:
            plt.yscale('log')

        savefig('aggregate_daily_paths.png')

        return None
