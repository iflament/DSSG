import pandas as pd
import numpy as np
from plotly.graph_objs import *
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from config import constants, logger_config, _data_dir
import logging.config
import logging
import credentials

plotly.tools.set_credentials_file(username=credentials.plotlyu,
                                  api_key=credentials.plotlykey)
logger = logging.getLogger(__name__)


class SiteAnalysis:
    
    """Analysis of entries in a specific site"""

    logging.config.dictConfig(logger_config)

    def __init__(self, click_params, params, data_feature_extracted):

        self.click_params = click_params
        self.params = params
        self.data = data_feature_extracted
        self._plot_site_visited_per_card('number-sites-per-card')
        self._plot_site_aggregate_entries('site-aggregate-entries')
        self._get_site_entries_per_timedelta(tdr_timedelta='date')
        self._get_site_entries_per_timedelta(tdr_timedelta='hour')
        self._get_site_entries_per_timedelta(tdr_timedelta='day_of_week')

    @staticmethod
    def _interpolate_on_timedelta(df, timedelta, timedelta_range,
                                  timeunit, start_date, end_date):
        """Interpolate data on a given timedelta"""

        df_interpolated = pd.DataFrame()

        if timedelta == 'day_of_week' or timedelta == 'hour':
            data = pd.DataFrame({timedelta: range(timedelta_range),
                                 'site_id': [id] * timedelta_range})
            df_interpolated = data.merge(df, how='right', on=['site_id', timedelta])
            df_interpolated = df_interpolated.fillna(0)

        if timedelta == 'date':
            columns = ['site_id', 'entrances_per_card_per_museum']
            data = pd.DataFrame(0, np.arange(timedelta_range), columns)
            full_id_days = data.reindex(
                pd.MultiIndex.from_product(
                    [df['site_id'].unique(),
                     pd.date_range(start_date, end_date,
                                   freq=timeunit)]
                ), fill_value=0
            )
            full_id_days = full_id_days.reset_index()
            full_id_days.columns = ['drop this', timedelta, 'site_id',
                                    'entrances_per_card_per_site']
            full_id_days = full_id_days.drop('drop this', 1)
            df_interpolated = pd.merge(
                full_id_days,
                df,
                how='right',
                on=['site_id', 'entrances_per_card_per_site', timedelta]
            )

        return df_interpolated

    def _get_site_entries_per_timedelta(self, tdr_timedelta):
        """Get site timeseries for a given timedelta and plot"""

        timedelta_range, timeunit = self._get_timedelta_range(tdr_timedelta)
        site_dfs = {}
        site_list = constants.site_list
        site_list.append('All Sites')

        for site_name in site_list[:]:

            if site_name != 'All Sites':
                df2 = self.data[self.data['site_name'].str.contains(site_name)]
            else:
                df2 = self.data

            df2 = df2.groupby(['site_id', 'site_name', tdr_timedelta], as_index=False)[
                'entrances_per_card_per_site'].sum()
            df_interpolated = self._interpolate_on_timedelta(
                df2,
                tdr_timedelta,
                timedelta_range,
                timeunit,
                self.params.site_start_date,
                self.params.site_end_date
            )
            df_interpolated = df_interpolated.rename(
                columns={'entrances_per_card_per_site': 'total_entries'}
            )
            df_interpolated['total_entries'] = df_interpolated['total_entries'].fillna(0)
            df_interpolated = df_interpolated.groupby(
                [tdr_timedelta, 'site_id'],
                as_index=False
            )['total_entries'].sum()
            site_dfs[site_name] = df_interpolated

        return site_dfs

    def _get_timedelta_range(self, tdr_timedelta):
        """Get timedelta range and unit for generating site timeseries """

        timeunit = pd.DataFrame()
        timedelta_range = pd.DataFrame()

        if tdr_timedelta == 'day_of_week':
            timedelta_range = 7
            timeunit = []

        if tdr_timedelta == 'hour':
            timedelta_range = 24
            timeunit = []

        if tdr_timedelta == 'date':
            delta = pd.to_datetime(self.params.site_end_date) - \
                    pd.to_datetime(self.params.site_start_date)
            timedelta_range = delta.days
            timeunit = 'D'

        return timedelta_range, timeunit

    def _plot_geomap_timeseries(self, plotname):
        """Plot geographical mapbox of timeseries data, for a given day"""

        df = self.data[self.data['date'] == self.params.site_date_to_plot]
        df = df[['site_id', 'latitude', 'longitude', 'site_name']].drop_duplicates()
        df = pd.merge(df, self.data.hour, on=['site_id'], how='inner')
        df = df[[self.params.site_geomap_timedelta, "total_entries", 'latitude',
                 'longitude', 'site_name']]

        df['site_name'][df.total_entries == 0] = float('nan')
        df['latitude'][df.total_entries == 0] = float('nan')
        df['longitude'][df.total_entries == 0] = float('nan')
        df.set_index('site_name', inplace=True)
        df['site_name'] = df.index
        df['name_entries'] = df['site_name'].astype(str) + ': ' + df['total_entries'].astype(str)
        df = df[df.hour >= self.params.site_min_timedelta]
        df = df[df.hour <= self.params.site_max_timedelta]

        data = []
        for hour in list(df[self.params.site_geomap_timedelta].unique()):
            trace = dict(
                lat=df[df[self.params.site_geomap_timedelta] == hour]['latitude'],
                lon=df[df[self.params.site_geomap_timedelta] == hour]['longitude'],
                name=hour,
                mode='marker',
                marker=dict(size=7),
                text=df[df[self.params.site_geomap_timedelta] == hour]['name_entries'],
                type='scattermapbox',
                hoverinfo='text'
            )

            data.append(trace)

        sites = list([
            dict(
                args=[{
                    'mapbox.center.lat': self.params.site_center_latitude,
                    'mapbox.center.lon': self.params.site_center_longitude,
                    'mapbox.zoom': 12,
                    'annotations[0].text': f'Sites of {self.click_params.city}'
                }],
                label=self.click_params.city,
                method='relayout'
            )
        ])

        m = df[['latitude', 'longitude']].drop_duplicates()
        for site, row in m.iterrows():
            desc = []
            for col in m.columns:
                if col not in ['latitude', 'longitude']:
                    if str(row[col]) not in ['None', 'nan', '']:
                        desc.append(col + ': ' + str(row[col]).strip("'"))
            desc.insert(0, site)
            sites.append(
                dict(
                    args=[{
                        'mapbox.center.lat': row['latitude'],
                        'mapbox.center.lon': float(str(row['longitude']).strip("'")),
                        'mapbox.zoom': 14,
                    }],
                    label=site,
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
                accesstoken=self.params.site_mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=self.params.site_center_latitude,
                    lon=self.params.site_center_longitude
                ),
                pitch=0,
                zoom=12
            ),
        )

        layout['updatemenus'] = updatemenus
        fig = dict(data=data, layout=layout)
        plot_url = py.iplot(fig, filename=plotname, sharing='private', auto_open=False)

        return df, plot_url

    def _plot_site_monthly_timeseries(self, plotname):
        """Plot Site monthly aggregate timeseries."""

        df = pd.DataFrame()

        trace1 = Bar(
            x=df.month,
            y=self.data,
            name=''
        )

        fig = go.Figure(data=go.Data([trace1]))
        plot_url = py.iplot(fig, filename=plotname, sharing='private')

        return df, plot_url

    def _get_timelines_of_usage(self):
        """Get timelines of usage of site data."""

        df_hour = self.data.hour[(self.data.hour['hour'] >= self.params.site_hour_min) &
                                 (self.data.hour['hour'] <= self.params.site_hour_max)]
        df_date = self.data.date.groupby('date', as_index=False)['total_entries'].mean()
        df_hour = df_hour.groupby('hour', as_index=False)['total_entries'].mean()
        df_dow = self.data.dow.groupby('day_of_week', as_index=False)['total_entries'].mean()

        return df_date, df_hour, df_dow

    def _plot_site_aggregate_entries(self, plotname):
        """Plot total site entries over summer 2016 per site."""

        df = self.data.groupby('site_name', as_index=True).sum()['total_people'].to_frame()
        df.sort_values('total_people', inplace=True, ascending=True)

        layout = go.Layout(
            title="Total Site Entries over summer 2016",
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

    def _plot_site_visited_per_card(self, plotname):
        """Plot frequency plot of number of unique sites visited per user"""

        df = self.data[['user_id', 'entry_is_adult', 'site_id', 'date']]
        df = df.groupby(['user_id'], as_index=True).site_id.nunique().\
            rename('total_sites_per_card').to_frame()

        trace1 = go.Histogram(
            x=df.total_sites_per_card,
            xbins=dict(start=np.min(df.total_sites_per_card) - 0.25,
                       size=0.5,
                       end=np.max(df.total_sites_per_card)
                       ),
            marker=dict(color='#CC171D')
        )

        layout = go.Layout(
            title="Total number of sites visited per card",
            xaxis=dict(
                title='Number of Sites',
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

