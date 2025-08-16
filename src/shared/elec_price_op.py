import pandas as pd
from datetime import time
import shared.apply_festivos_omie as apply_festivos_omie
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import utils.utils_dates as utils_dates

from config.config_loader import Config

# config = Config()

class SpotElec:

    def __init__(self, df: pd.DataFrame):

        df['datetime'] = pd.to_datetime(df['datetime'])
        self.df = df.copy()

    def format(self):

        if self.df is not None and not self.df.empty:

            try:
                df = self.df.copy()
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['date'] = df['datetime'].apply(lambda x: x.date())
                df['month'] = df['datetime'].apply(lambda x: x.month)
                df['year'] = df['datetime'].apply(lambda x: x.year)
            except KeyError:
                print("The expected 'values' field was not found in the response.")
                raise KeyError("The 'values' field is missing from the response data.")
            except IndexError:
                print("The structure of the 'values' field is not as expected.")
                raise IndexError("Failed to extract data from the 'values' field.")
            self.df_clean = df
            
        else:
            print('No data to clean. Empty DataFrame returned.')
            df = pd.DataFrame()  
        
        return self
    
    
    def apply_periodos (self, periodos_path, festivos_path):

        try:
            self.df_w_periodos.copy()
            print('Periodos already applied to SpotElec')
            return self
        except:
            df_spot = self.df_clean.copy()


        df_periodos = pd.read_excel(periodos_path)
        df_periodos.set_index(df_periodos.columns[0], inplace=True)
        df_periodos = df_periodos.T
        df_periodos.index = df_periodos.index.map(lambda x: time((x),0,0))

        df_festivos = apply_festivos_omie.apply_festivos(festivos_path)

        df_spot['time'] = df_spot['datetime'].apply(lambda x: x.time())
        df_spot['date'] = df_spot['datetime'].apply(lambda x: x.date())
        df_spot['month'] = df_spot['datetime'].apply(lambda x: x.month)
        df_spot['year'] = df_spot['datetime'].apply(lambda x: x.year)

        df_spot['periodo'] = \
            df_spot.apply(lambda row: df_periodos.loc[time(row['time'].hour,0), row['month']], axis=1)
            # df_spot.apply(lambda row: df_periodos.loc[row['time'], row['month']], axis=1)

        df_spot['periodo'] = df_spot.apply(
            lambda row: 6 if row['date'] in df_festivos['date'].values else row['periodo'], axis=1
        )
        df_spot['periodo'] = df_spot.apply(
            lambda row: 6 if ((row['date'].weekday() == 6) or 
            (row['date'].weekday() == 5))
            else row['periodo'], axis=1
        )
        self.df_w_periodos = df_spot
        return self
    
    def filter_df (self, end_date= None, start_date=None, months=None, years=None):

        try:
            df_filtered = self.df_w_periodos.copy()
        except:
            print('Warning: apply_periodos method not applied to SpotElec instance')
            return self

        if end_date:
            df_filtered =  df_filtered[(df_filtered['date'] <= end_date)]
        if start_date:
            df_filtered = df_filtered[(df_filtered['date'] >= start_date)]
        if months:
            df_filtered = df_filtered[(df_filtered['month'].isin(months))]
        if years:
            df_filtered = df_filtered[(df_filtered['year'].isin(years))]

        self.df_filtered = df_filtered

        return self
    
    def spot_mensual (self):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()
            
        ds = df.groupby(['year', 'month'])['value'].mean()
        df2 = pd.DataFrame(ds)
        df2 = df2.reset_index()
        df_pivot = df2.pivot(index='year', columns='month', values='value')
        return df_pivot
    
    def spot_hour_mensual_stats(self):
    
        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()
            
        # Group by year, month, and time; calculate mean, min, and max
        grouped = df.groupby(['year', 'month', 'time'])['value'].agg(['mean', 'min', 'max'])

        # Reset index to make it easier to work with
        grouped = grouped.reset_index()

        # Pivot the DataFrame to create a MultiIndex DataFrame
        df_pivot = grouped.pivot(index=['year', 'month'], columns='time')

        return df_pivot
        
    def spot_q (self):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()
            
        ds = df.groupby(['year', 'month'])['value'].mean()
        df2 = pd.DataFrame(ds)
        df2 = df2.reset_index(drop=False)
        df2['q'] = df2['month'].apply(lambda x: utils_dates.obtener_trimestre(x))
        df2 = df2.drop('month', axis=1)
        ds2 = df2.groupby(['year', 'q']).mean()
        df3 = pd.DataFrame(ds2)

        df3 = df3.reset_index()
        df_pivot = df3.pivot(index='year', columns='q', values='value')
        return df_pivot
    
    def spot_mensual_periodos (self):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()

        ds = df.groupby(['year' ,'month', 'periodo'])['value'].mean()
        df2 = pd.DataFrame(ds)
        df2 = df2.reset_index()
        df_pivot = df2.pivot(index=['year', 'month'], columns='periodo', values='value')
        df_pivot = df_pivot.reindex(columns=[1, 2, 3, 4, 5, 6])
        df_pivot.columns = [f'P{col}' for col in df_pivot.columns]
        df_pivot = df_pivot.reset_index()
        
        return df_pivot
    
    def spot_negativo(self):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()

        df_fil = df[df['value'] <= 0]

        ds = df_fil.groupby(['year' ,'month'])['value'].count()
        df2 = pd.DataFrame(ds)
        df2 = df2.reset_index()
        df_pivot = df2.pivot(index='year', columns='month', values='value')
        df_pivot = df_pivot.reset_index()

        return df_pivot
    
    def spot_intervalo(self,
                        upper= float('+inf'),
                        upper_include= False,
                        lower= float('-inf'),
                        lower_include= True
                        ):
        
        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()
        
        if lower_include and upper_include:
            df_fil = df[(df['value'] >= lower) & (df['value'] <= upper)]
        elif lower_include and not upper_include:
            df_fil = df[(df['value'] >= lower) & (df['value'] < upper)]
        elif not lower_include and upper_include:
            df_fil = df[(df['value'] > lower) & (df['value'] <= upper)]
        else:
            df_fil = df[(df['value'] > lower) & (df['value'] < upper)]

        ds = df_fil.groupby(['year' ,'month'])['value'].count()
        df2 = pd.DataFrame(ds)
        df2 = df2.reset_index()
        df_pivot = df2.pivot(index='year', columns='month', values='value')
        df_pivot = df_pivot.reset_index()

        return df_pivot
    
    def apuntamientos_periodo (self, attr: {'mensual', 'diario'}, filter: bool):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()
        
        daily_avg = df.groupby('date')['value'].mean().reset_index()
        daily_avg.rename(columns={'value': 'day_avg'}, inplace=True)

        df = pd.merge(df, daily_avg, on='date', how='left')
        df['apuntamiento'] = df.apply(lambda row: row['value'] / row['day_avg'], axis=1)

        spot_mensual_periodo = df.groupby(['year' ,'month', 'periodo'])['value'].mean()
        spot_mensual_periodo = pd.DataFrame(spot_mensual_periodo)
        apuntamiento_d = df.groupby(['year', 'month', 'periodo'])['apuntamiento'].mean()
        apuntamiento_m = df.groupby(['year', 'month', 'periodo'])['value'].mean() / df.groupby(['year', 'month'])['value'].mean()
        df_apuntamientos = pd.concat([spot_mensual_periodo, apuntamiento_d, apuntamiento_m], axis=1)
        df_apuntamientos = df_apuntamientos.reset_index()
        df_apuntamientos.columns = ['year', 'month', 'periodo', 'spot_mensual', 'ponderado_diario', 'ponderado_mensual']

        try:
            df_pivot = df_apuntamientos.pivot(index=['year', 'month'], columns='periodo', values=f'ponderado_{attr}')
            df_pivot = df_pivot.reindex(columns=[1, 2, 3, 4, 5, 6])
            df_pivot.columns = [f'P{col}' for col in df_pivot.columns]
            df_pivot = df_pivot.reset_index()
        except:
            print('Attribute must be either "mensual" or "diario"')
            return pd.DataFrame()

        if filter == True:
            if attr == 'mensual':
                df_pivot_filter = df_pivot.tail(13).reset_index(drop=True)
                df_pivot_filter = df_pivot_filter.iloc[:12,:]
                df_pivot_filter = df_pivot_filter.drop('year', axis=1).sort_values('month').reset_index(drop=True)
            elif attr == 'diario':
                df_pivot_filter = df_pivot.tail(12).sort_values('month').reset_index(drop=True)
                df_pivot_filter = df_pivot_filter.drop('year', axis=1)
            return df_pivot_filter
        else:
            return df_pivot
    
    def apuntamientos_hour_mensual(self):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()

        daily_avg = df.groupby('date')['value'].mean().reset_index()
        daily_avg.rename(columns={'value': 'day_avg'}, inplace=True)

        df = pd.merge(df, daily_avg, on='date', how='left')
        df['cap_rate'] = df['value'] / df['day_avg']
        ds = df.groupby(['year', 'month', 'time'])['cap_rate'].mean()

        df_ap_h = pd.DataFrame(ds)
        df_ap_h.reset_index(inplace=True)
        # df_ap_h.columns = ['year', 'month', 'cap_rate']
        df_pivot = df_ap_h.pivot(index=['year', 'month'], columns='time', values=f'cap_rate')
        return df_pivot
    
    def precio_solar (self):

        try:
            df = self.df_filtered.copy()
        except:
            df = self.df_w_periodos.copy()

        df = df[(df['time'] <= time(20,0)) & (df['time'] >= time(8,0))]
        ds = df.groupby('date')['value'].mean()
        df1 = pd.DataFrame(ds)
        df1 = df1.reset_index()
        df1['month'] = df1['date'].apply(lambda x: x.month)
        df1['year'] = df1['date'].apply(lambda x: x.year)
        df1 = df1[['date', 'month', 'year', 'value']]

        self.df_solar = df1

        return self
    def m (self):

        df = self.df_solar
        ds = df.groupby(['month', 'year'])['value'].mean()
        df1 = pd.DataFrame(ds)
        df1 = df1.reset_index()
        df_pivot = df1.pivot(index='year', columns='month', values='value')
        return df_pivot
    
    def q (self):

        df = self.df_solar
            
        ds = df.groupby(['year', 'month'])['value'].mean()
        df2 = pd.DataFrame(ds)
        df2 = df2.reset_index(drop=False)
        df2['q'] = df2['month'].apply(lambda x: utils_dates.obtener_trimestre(x))
        df2 = df2.drop('month', axis=1)
        ds2 = df2.groupby(['year', 'q']).mean()
        df3 = pd.DataFrame(ds2)

        df3 = df3.reset_index()
        df_pivot = df3.pivot(index='year', columns='q', values='value')
        return df_pivot

class FuturesElec:

    def __init__(self, df_futures):

        self.df_futures = df_futures
        
    def plot_single_product(self, product, config_path:str, percentiles=[10, 50, 75]):

        config = Config(config_file=config_path)
        df = self.df_futures.copy()
        # Filter the DataFrame based on the product
        df_filtered = df[df['Contract'] == product]

        # Create the line plot using Plotly Express
        fig = px.line(df_filtered, x='Day', y='SettlementPrice', title=f'Settlement Price {product}')

        # Convert the Express figure to a graph_objects figure for further customization
        fig = go.Figure(fig)

        fig.data[0].line.color = '#14AFAB'
        # #012e41
        # Calculate the percentiles for SettlementPrice
        price_percentiles = df_filtered['SettlementPrice'].quantile([p/100 for p in percentiles])

        # Add horizontal lines for each percentile
        for percentile, value in zip(percentiles, price_percentiles):
            # Add a horizontal line for each percentile
            fig.add_shape(
                type='line',
                xref='paper', yref='y',
                x0=0, x1=1, y0=value, y1=value,
                line=dict(color="#0F4C81", width=2, dash='dash'),
                opacity=0.7,
                layer='above',  # Ensures the line is visible above the plot
                name=f'{percentile}th Percentile'
            )

        # Remove in-plot annotations for percentiles
        # Instead, add text annotations outside the plot area
        # Positioning outside the plot to the right side
        annotations = []
        y_offset = 1.15  # Adjust this value to position the annotations higher or lower

        for i, (percentile, value) in enumerate(zip(percentiles, price_percentiles)):
            annotations.append(
                dict(
                    xref='paper', yref='paper',
                    x=1.02, y=y_offset - i * 0.1,  # Adjust x and y for position outside the plot
                    text=f'{percentile}th Percentile: {value:.2f}',
                    showarrow=False,
                    font=dict(color="#0F4C81"),
                    bgcolor="white",
                    bordercolor="#0F4C81",
                    borderwidth=1,
                    borderpad=4
                )
            )

        # Add all annotations to the figure
        fig.update_layout(annotations=annotations)

        # Adjust the layout for better visibility
        fig.update_layout(
            hovermode='x',  # Enable hover mode on the x-axis
            xaxis_title='Day',
            yaxis_title='SettlementPrice [€/MWh]',
            title={
                'text': f'Settlement Price {product}',
                'y': 0.9,
                'x': 0.25,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(  # Set font for the title
                    family="Montserrat, sans-serif",  # Specify Montserrat font
                    size=20,  # Font size (adjust as needed)
                    color="#012e41",  # Font color
                    weight="bold"
                )
            },
            xaxis=dict(
                title=dict(
                    text="Day",  # X-axis title
                    font=dict(
                        family="Montserrat, sans-serif",  # Montserrat font
                        size=16,  # Font size
                        color="#012e41",  # Font color #C2C7CA grey
                        weight="normal"  # Bold font
                    )
                )
            ),
            yaxis=dict(
                title=dict(
                    text="[€/MWh]",  # Y-axis title
                    font=dict(
                        family="Montserrat, sans-serif",  # Montserrat font
                        size=16,  # Font size
                        color="#012e41",  # Font color
                        weight="normal"  # Bold font
                    )
                )
            ),
            # margin=dict(l=50, r=150, t=80, b=50)  # Add extra space on the right for annotations
        )

        # Add custom hover interaction
        fig.update_traces(mode='lines', hovertemplate='Date: %{x}<br>Settlement Price: %{y:.2f}')

        fig.write_html(config.get_path("outputs.markets.elec.graphs.html", name=f"Graph {product}"))
        # Show the plot
        fig.show()