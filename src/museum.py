
import pandas as pd
import numpy as np
from plotly.graph_objs import *
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from config import constants, logger_config, _export_dir
import logging.config
import logging
import credentials

plotly.tools.set_credentials_file(username=credentials.plotlyu, api_key=credentials.plotlykey)
logger = logging.getLogger(__name__)


class MuseumAnalysis:
    
    """Analysis of entries in a specific site"""

    logging.config.dictConfig(logger_config)

    def __init__(self, params, data_feature_extracted):

        self.params = params
        self.data = data_feature_extracted

        self._plot_day_of_activation('day_of_activation-test')
        self._plot_museums_visited_per_card('number-museums-per-card-test')
        self._plot_museum_aggregate_entries('museum-aggregate-entries-test')
        self._get_museum_entries_per_timedelta(tdr_timedelta='date')
        self._get_museum_entries_per_timedelta(tdr_timedelta='hour')
        self._get_museum_entries_per_timedelta(tdr_timedelta='day_of_week')

    @staticmethod
    def _interpolate_on_timedelta(df, timedelta, timedelta_range, timeunit, start_date, end_date):
        """Interpolate data on a given timedelta"""

        df_interpolated = pd.DataFrame()

        if timedelta == 'day_of_week' or timedelta == 'hour':
            data = pd.DataFrame({timedelta: range(timedelta_range), 'museum_id': [id] * timedelta_range})
            df_interpolated = data.merge(df, how='right', on=['museum_id', timedelta])
            df_interpolated = df_interpolated.fillna(0)

        if timedelta == 'date':
            columns = ['museum_id', 'entrances_per_card_per_museum']
            data = pd.DataFrame(0, np.arange(timedelta_range), columns)
            full_id_days = data.reindex(pd.MultiIndex.from_product([df['museum_id'].unique(),
                                                                    pd.date_range(start_date, end_date,
                                                                                  freq=timeunit)]), fill_value=0)
            full_id_days = full_id_days.reset_index()
            full_id_days.columns = ['drop this', timedelta, 'museum_id', 'entrances_per_card_per_museum']
            full_id_days = full_id_days.drop('drop this', 1)
            df_interpolated = pd.merge(full_id_days, df, how='right',
                                       on=['museum_id', 'entrances_per_card_per_museum', timedelta])

        return df_interpolated

    def _get_museum_entries_per_timedelta(self, tdr_timedelta):
        """Get museum timeseries for a given timedelta and plot"""

        timedelta_range, timeunit = self._get_timedelta_range(tdr_timedelta)
        museum_dfs = {}

        for museum_name in constants.museum_list[:]:

            if museum_name != 'All Museums':
                df2 = self.data[self.data['museum_name'].str.contains(museum_name)]
            else:
                df2 = self.data

            df2 = df2.groupby(['museum_id', 'museum_name', tdr_timedelta], as_index=False)[
                'entrances_per_card_per_museum'].sum()
            df_interpolated = self._interpolate_on_timedelta(df2, tdr_timedelta, timedelta_range, timeunit,
                                                             self.params.fc_start_date, self.params.fc_end_date)
            df_interpolated = df_interpolated.rename(columns={'entrances_per_card_per_museum': 'total_entries'})
            df_interpolated['total_entries'] = df_interpolated['total_entries'].fillna(0)
            df_interpolated = df_interpolated.groupby([tdr_timedelta, 'museum_id'], as_index=False)['total_entries'].sum()
            museum_dfs[museum_name] = df_interpolated

        return museum_dfs

    def _get_timedelta_range(self, tdr_timedelta):
        """Get timedelta range and unit for generating museum timeseries (called by
        get_museum_entries_per_timedelta_and_plot)"""

        timeunit = pd.DataFrame()
        timedelta_range = pd.DataFrame()

        if tdr_timedelta == 'day_of_week':
            timedelta_range = 7
            timeunit = []

        if tdr_timedelta == 'hour':
            timedelta_range = 24
            timeunit = []

        if tdr_timedelta == 'date':
            delta = pd.to_datetime(self.params.fc_end_date) - pd.to_datetime(self.params.fc_start_date)
            timedelta_range = delta.days
            timeunit = 'D'

        return timedelta_range, timeunit

    def _plot_geomap_timeseries(self, plotname):
        """Plot geographical mapbox of timeseries data, for a given day"""

        df = self.data[self.data['date'] == self.params.fc_date_to_plot]
        df = df[['museum_id', 'latitude', 'longitude', 'short_name']].drop_duplicates()
        df = pd.merge(df, self.data.hour, on=['museum_id'], how='inner')
        df = df[[self.params.fc_geomap_timedelta, "total_entries", 'latitude', 'longitude', 'short_name']]

        df['short_name'][df.total_entries == 0] = float('nan')
        df['latitude'][df.total_entries == 0] = float('nan')
        df['longitude'][df.total_entries == 0] = float('nan')
        df.set_index('short_name', inplace=True)
        df['short_name'] = df.index
        df['name_entries'] = df['short_name'].astype(str) + ': ' + df['total_entries'].astype(str)
        df = df[df.hour >= self.params.fc_min_timedelta]
        df = df[df.hour <= self.params.fc_max_timedelta]

        data = []
        for hour in list(df[self.params.fc_geomap_timedelta].unique()):
            trace = dict(
                lat=df[df[self.params.fc_geomap_timedelta] == hour]['latitude'],
                lon=df[df[self.params.fc_geomap_timedelta] == hour]['longitude'],
                name=hour,
                mode='marker',
                marker=dict(size=7),
                text=df[df[self.params.fc_geomap_timedelta] == hour]['name_entries'],
                type='scattermapbox',
                hoverinfo='text'
            )

            data.append(trace)

        museums = list([
            dict(
                args=[{
                    'mapbox.center.lat': 43.768, #lat of center of florence
                    'mapbox.center.lon': 11.262, #lon of center of florence
                    'mapbox.zoom': 12,
                    'annotations[0].text': 'Museums in Florence'
                }],
                label='Florence',
                method='relayout'
            )
        ])

        m = df[['latitude', 'longitude']].drop_duplicates()
        for museum, row in m.iterrows():
            desc = []
            for col in m.columns:
                if col not in ['latitude', 'longitude']:
                    if str(row[col]) not in ['None', 'nan', '']:
                        desc.append(col + ': ' + str(row[col]).strip("'"))
            desc.insert(0, museum)
            museums.append(
                dict(
                    args=[{
                        'mapbox.center.lat': row['latitude'],
                        'mapbox.center.lon': float(str(row['longitude']).strip("'")),
                        'mapbox.zoom': 14,
                    }],
                    label=museum,
                    method='relayout'
                )
            )

        updatemenus = list([
            dict(
                buttons=list([
                    dict(
                        args=['mapbox.style', 'light'],
                        label='Map',
                        method='relayout'
                    ),
                    dict(
                        args=['mapbox.style', 'satellite-streets'],
                        label='Satellite',
                        method='relayout'
                    )
                ]),
                direction='up',
                x=0.75,
                xanchor='left',
                y=0.05,
                yanchor='bottom',
                bgcolor='#ffffff',
                bordercolor='#000000',
                font=dict(size=11)
            ),
        ])

        layout = Layout(
            showlegend=True,
            autosize=False,
            hovermode='closest',
            mapbox=dict(
                accesstoken=self.params.fc_mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=43.768,
                    lon=11.262
                ),
                pitch=0,
                zoom=12
            ),
        )

        layout['updatemenus'] = updatemenus
        fig = dict(data=data, layout=layout)
        plot_url = py.iplot(fig, filename=plotname, sharing='private', auto_open=False)

        return df, plot_url

    def _plot_museum_monthly_timeseries(self, plotname):
        """Plot Firenzecard and State Museum monthly aggregate timeseries."""

        df = pd.DataFrame()

        trace1 = Bar(
            x=df.month,
            y=self.data,
            name='FirenzeCard'
        )

        trace2 = Bar(
            x=df.month,
            y=self.data,
            name='State Museums'
        )

        fig = go.Figure(data=go.Data([trace1, trace2]))
        plot_url = py.iplot(fig, filename=plotname, sharing='private')

        return df, plot_url

    def _get_timelines_of_usage(self):
        """Get timelines of usage of Firenzecard data."""

        df_hour = self.data.hour[(self.data.hour['hour'] >= self.params.fc_hour_min) &
                                 (self.data.hour['hour'] <= self.params.fc_hour_max)]
        df_date = self.data.date.groupby('date', as_index=False)['total_entries'].mean()
        df_hour = df_hour.groupby('hour', as_index=False)['total_entries'].mean()
        df_dow = self.data.dow.groupby('day_of_week', as_index=False)['total_entries'].mean()

        return df_date, df_hour, df_dow

    def _plot_museum_aggregate_entries(self, plotname):
        """Plot total museum entries over summer 2016 per museum."""

        df = self.data.groupby('short_name', as_index=True).sum()['total_people'].to_frame()
        df.sort_values('total_people', inplace=True, ascending=True)

        layout = go.Layout(
            title="Total Museum Entries over summer 2016",
            xaxis=dict(
                title='',
                ticks='outside',
            ),
            yaxis=dict(
                title='Total Number of Entries',
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

    def _plot_museums_visited_per_card(self, plotname):
        """Plot frequency plot of number of unique museums visited per card"""

        df = self.data[['user_id', 'entry_is_adult', 'museum_id', 'date']]
        df = df.groupby(['user_id'], as_index=True).museum_id.nunique().rename('total_museums_per_card').to_frame()

        trace1 = go.Histogram(x=df.total_museums_per_card, xbins=dict(start=np.min(df.total_museums_per_card) - 0.25,
                                                                      size=0.5,
                                                                      end=np.max(df.total_museums_per_card)),
                              marker=dict(color='#CC171D'))

        layout = go.Layout(
            title="Total number of museums visited per card",
            xaxis=dict(
                title='Number of Museums',
                nticks=7,
                ticks='outside',
            ),
            yaxis=dict(
                title='Number of Cards',
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

        fig = go.Figure(data=go.Data([trace1]), layout=layout)
        plot_url = py.iplot(fig, filename=plotname, sharing='private', auto_open=False)

        return df, plot_url

    def _plot_day_of_activation(self, plotname):
        """Plots Aggregate of Day of Activation."""

        # todo sort order in logical day order
        dotw = {0: 'Monday',
                1: 'Tuesday',
                2: 'Wednesday',
                3: 'Thursday',
                4: 'Friday',
                5: 'Saturday',
                6: 'Sunday'}
        df = self.data[self.data['adults_first_use'] == 1][['user_id', 'day_of_week']]
        df = df.groupby('user_id', as_index=False).mean()['day_of_week'].map(dotw).to_frame()
        df = df['day_of_week'].value_counts().to_frame()

        # todo fix the X axis labeling so it's not hardcoded!
        trace = go.Bar(x=['Tuesday', 'Wednesday', 'Friday', 'Thursday', 'Saturday', 'Sunday', 'Monday'],
                       y=df.day_of_week,
                       marker=dict(color='#CC171D'))

        layout = go.Layout(
            title="Day of Firenze Card Activation",
            xaxis=dict(
                title='Day of the Week',
                nticks=7,
                ticks='outside',
            ),
            yaxis=dict(
                title='Number of Cards Activated',
                ticks='outside',
            )
        )
        fig = go.Figure(data=go.Data([trace]), layout=layout)
        plot_url = py.iplot(fig, filename=plotname, sharing='private', auto_open=False)

        return plot_url
