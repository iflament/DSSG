import pandas as pd
from plotly.graph_objs import *
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from config import constants, logger_config, _data_dir
import logging.config
import logging
import credentials

plotly.tools.set_credentials_file(username=credentials.plotlyu, api_key=credentials.plotlykey)
logger = logging.getLogger(__name__)


class CDRAnalysis:
    """CDR Analysis"""

    logging.config.dictConfig(logger_config)

    def __init__(self, params, data_feature_extracted):
        self.params = params
        self.data_feature_extracted = data_feature_extracted
        self.cdr_main(self.data_feature_extracted)

    @staticmethod
    def cdr_main(df):
        """ Exploratory analysis of CDR data """

        # Create a frequency count of how many average  daily calls each customer makes
        daily_calls = df.groupby(['user_id', 'date'], as_index=False).count()

        # Create a frequency count of how many average hourly calls each customer makes
        hourly_calls = df.groupby(['user_id', 'time'], as_index=False).count()

        # Count calls per customer
        calls_per_cust = df.groupby(['user_id'], as_index=False).count()

        # Total estimated daily presences: Italians & Foreigners
        # Make a stacked bar plot day by day through summer

        # Estimated daily presence of foreign visitors

        # Estimated daily presence of Italian visitors

        return None

    def _plot_tower_aggregate_entries(self, plotname):
        """Plot total site entries over summer 2016 per site."""

        df = self.data_feature_extracted.groupby('tower_id', as_index=True).sum()['total_people'].to_frame()
        df.sort_values('total_people', inplace=True, ascending=True)

        layout = go.Layout(
            title="Total people per call tower over summer 2016",
            xaxis=dict(
                title='',
                ticks='outside',
            ),
            yaxis=dict(
                title='Total Number of Users',
                ticks='outside',
            ),
            legend=dict(
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=12,
                    color='#000'
                ),
                bgcolor='#E2E2E2',
                bordercolor='#FFFFFF',
                borderwidth=2
            )
        )

        trace = Bar(
            x=df.index,
            y=df['total_people'],
            marker=dict(color='#CC171D'),
        )

        fig = go.Figure(data=go.Data([trace]), layout=layout)
        plot_url = py.iplot(fig, filename=plotname, sharing='private', auto_open=False)

        return df, plot_url

    def _plot_tower_monthly_timeseries(self, plotname):
        """Plot Site monthly aggregate timeseries."""

        df = pd.DataFrame()

        trace1 = Bar(
            x=df.month,
            y=self.data_feature_extracted,
            name=''
        )

        fig = go.Figure(data=go.Data([trace1]))
        plot_url = py.iplot(fig, filename=plotname, sharing='private')

        return df, plot_url













