from datetime import datetime, timedelta
import pandas as pd
from utils.utils_dates import obtener_trimestre
import numpy as np

class Liquidation:

    def __init__(self, 
                start_date: datetime,
                end_date: datetime,
                df_master: pd.DataFrame,
                df_contrato: pd.DataFrame,
                power_list: list,
                df_load: pd.DataFrame,
                df_coberturas: pd.DataFrame,
                 ) -> None:

        self.start_date = start_date
        self.end_date = end_date
        self.df_master = df_master
        self.df_load = df_load
        self.df_coberturas = df_coberturas
        self.power_list = power_list
        self.cups = df_master['cups'].unique()[0]
        self.cliente = df_master['cliente'].unique()[0]
        self.dto_electrointensivos = 0
        self.click = False
        self.click_columns = ['load_base_click', 'perc_click', 'price_click']


        df_contrato_fil = df_contrato[
                        (df_contrato['datetime'].dt.date >= (start_date.date())) &
                        (df_contrato['datetime'].dt.date <= (end_date.date()))
                        ]
        self.df_contrato = df_contrato_fil

        self.aps_dict = {
            'Q' : 'Ap_fixed_quarter',
            'M' : 'Ap_fixed_month',
            'YR' : 'Ap_fixed_year'
        }

        # queda desarrollar el caso en el que para un tramo, haya más de una forma de liquidación
        # para ello, hay que calcular self.contract_code con .apply, fila a fila

    def _merge_master_load(self):

        df_master = self.df_master.copy()
        df_load = self.df_load.copy()

        df_master_fil = df_master[
            (df_master['datetime'] >= self.start_date) & (df_master['datetime'] <= self.end_date)
            ]

        df_master_fil = df_master_fil.copy()
        df_master_fil.loc[:, 'dup'] = df_master_fil.groupby('datetime').cumcount()

        df_load_fil = df_load[
            (df_load['datetime'] >= self.start_date) & (df_load['datetime'] <= self.end_date) & 
            (df_load['resolution'] == 'hourly') & (df_load['cups'] == self.cups)
            ]
        df_load_fil = df_load_fil[['cups', 'datetime', 'periodo', 'load']]
        df_load_fil.loc[:, 'dup'] = df_load_fil.groupby('datetime').cumcount()

        df_verif = pd.merge(df_master_fil, df_load_fil, on=['cups', 'datetime', 'periodo', 'dup'], how='left')
        df_verif.drop('dup', axis=1, inplace=True)

        self.df_verif = df_verif

        return self
        
    def execute(self, contract_mapping: dict):

        self._merge_master_load()
        contract_index = self.df_verif['contract_id'].unique()[0]
        contract_id = self.df_verif['contract_index'].unique()[0] # hay que cambiar y obtener coste_unitario con .apply()
        self.contract_code = f'{self.cliente}_{contract_index}_{contract_id}'
        self._get_quarter_load()
        self._merge_power_to_quarter_load()
        self._calculate_power_cost()
        self._calculate_power_excess()
        self._apply_coberturas()
        self._apply_formula(contract_mapping)
        self._calculate_dto_electrointensivos()
        self._get_capture_kpis()

        self.df_verif['coste_total'] = self.df_verif['coste_unitario'] * self.df_verif['load'] / 1000
        self.coste_energia = self.df_verif['coste_total'].sum()
        self.base_sin_ie = (self.df_verif['coste_total'].sum() + self.coste_potencia + self.excesos_potencia  - self.dto_electrointensivos)
        self.ie = self.base_sin_ie * (self.df_verif['ie']).mean()
        self.base_imponible = self.base_sin_ie + self.ie

        return self

    def _get_quarter_load(self):

        df_load = self.df_load.copy()
        df_contrato = self.df_contrato.copy()

        df_load_fil = df_load[
            (df_load['datetime'] >= self.start_date) & (df_load['datetime'] < (self.end_date + timedelta(hours=1))) & 
            (df_load['cups'] == self.cups)
            ]
        df_load_quarter = df_load_fil[(df_load_fil['resolution'] == 'quarter-hourly')]

        if not df_load_quarter.empty:
            df_load_quarter = df_load_quarter.copy()
            df_load_quarter['load'] = df_load_quarter['load'] * 4
        else:
            df_load_quarter = df_load_fil[(df_load_fil['resolution'] == 'hourly')]

        df_load_quarter.sort_values(by='datetime', inplace=True)

        df_contrato['date'] = df_contrato['datetime'].dt.date
        df_load_quarter['date'] = df_load_quarter['datetime'].dt.date
        
        df_power_parameters = df_contrato[['date', 'periodo', 'tep_power_exc', 'kp_power_exc']]
        df_load_quarter = pd.merge(df_load_quarter, df_power_parameters, on=['date', 'periodo'], how='left')
        df_load_quarter.drop('date', axis=1, inplace=True)
        self.df_load_quarter = df_load_quarter
    
    def _merge_power_to_quarter_load(self):

        power_list = self.power_list.copy()
        df_load_quarter = self.df_load_quarter.copy()
        df_verif = self.df_verif.copy()

        df_power = pd.DataFrame(power_list, index=[period for period in range(1,7)])
        df_power.reset_index(inplace=True)
        df_power.columns = ['periodo', 'potencia']
        self.df_power = df_power
        df_load_quarter = pd.merge(df_load_quarter, df_power, on='periodo', how='left')
        df_verif = pd.merge(df_verif, df_power, on='periodo', how='left')
        self.df_load_quarter = df_load_quarter
        self.df_verif = df_verif
        
    def _read_coberturas(self, row):

        df_coberturas = self.df_coberturas.copy()
        year = row['datetime'].year
        month = row['datetime'].month
        
        df_coberturas_fil = df_coberturas[(df_coberturas['Año'] == year) &
                                        ((df_coberturas['Producto'] == ('Q' + str(obtener_trimestre(month)))) |
                                        (df_coberturas['Producto'] == ('M' + str(month))) |
                                        (df_coberturas['Producto'] == 'YR'))]
        porcentaje_list = df_coberturas_fil[df_coberturas_fil['Tipo'] == 'Porcentaje [%]']
        cargabase_list = df_coberturas_fil[df_coberturas_fil['Tipo'] == 'Carga Base [MW]']
        self.df_coberturas_fil = df_coberturas_fil

        if not porcentaje_list.empty:
            precio_pond = (df_coberturas_fil['Porcentaje [%]'] * df_coberturas_fil['Precio [€/MWh]']).sum() /\
                  df_coberturas_fil['Porcentaje [%]'].sum()
            perc_agg = df_coberturas_fil['Porcentaje [%]'].sum()

            return 0, perc_agg, precio_pond
            
        if not cargabase_list.empty:
            precio_pond = (df_coberturas_fil['Carga Base [MW]'] * df_coberturas_fil['Precio [€/MWh]']).sum() /\
                  df_coberturas_fil['Carga Base [MW]'].sum()
            power_agg = df_coberturas_fil['Carga Base [MW]'].sum()

            return power_agg, 0, precio_pond
        return 0, 0, 0
    
    def _calculate_power_excess(self):
        
        df_load_quarter = self.df_load_quarter.copy()
        df_load_quarter['input'] = df_load_quarter.apply(lambda group: (group['load'] - group['potencia']) ** 2
                                if (group['load'] - group['potencia'] > 0) else 0, axis=1)
        
        list_pw = df_load_quarter.groupby('periodo')['input'].sum()
        tep = df_load_quarter.groupby('periodo')['tep_power_exc'].mean()
        kp = df_load_quarter.groupby('periodo')['kp_power_exc'].mean()
        excesos_potencia = (np.sqrt(list_pw) * kp * tep).sum()

        self.excesos_potencia = excesos_potencia

    def _calculate_power_cost(self):

        df = self.df_contrato.copy()
        df_power = self.df_power.copy()
        df_contrato = pd.merge(df, df_power, on='periodo', how='left')
        coste_potencia = ((df_contrato['peajes_potencia'] + df_contrato['cargos_potencia']) \
                          * df_contrato['potencia']).sum()
        dto_electrointensivos_potencia = (df_contrato['dto_peajes_potencia'] * df_contrato['potencia']).sum()
        self.coste_potencia = coste_potencia
        self.dto_electrointensivos_potencia = dto_electrointensivos_potencia
    
    def _calculate_dto_electrointensivos(self):

        df = self.df_verif.copy()
        dto_electrointensivos_energia = (df['dto_peajes_energia'] * df['load'] / 1000).sum()

        self.dto_electrointensivos = dto_electrointensivos_energia + self.dto_electrointensivos_potencia
    
    def _apply_coberturas(self):
        
        df_verif = self.df_verif.copy()

        df_verif[self.click_columns] = df_verif.apply(
            lambda row: pd.Series(self._read_coberturas(row)), axis=1
        )
        for col in self.click_columns:
            if df_verif[col].sum() > 0:
                self.click = True
                break

        # If no column met the condition, drop click_columns
        if not self.click:
            df_verif.drop(self.click_columns, axis=1, inplace=True)
        
        self.df_verif = df_verif
    
    def _map_periods(self, series):

        dict = series.to_dict()
        mapped_series = [dict.get(period, 0) for period in [period for period in range (1,7)]]
        return mapped_series
    
    def _get_capture_kpis(self):

        df = self.df_verif

        price = df.groupby(df['datetime'].dt.time).apply(
            lambda row: ((row['coste_unitario'] * row['load']).sum() / row['load'].sum())
            )
        price_captured_h = pd.DataFrame(price)

        cap_comm_price = ((df['value'] * df['load']).sum() / df['load'].sum())

        try:
            cap_comm_price_w_clicks = (((df['value'] * (1 - df['perc_click']) + df['price_click'] * df['perc_click'])\
                                        * df['load']).sum() / df['load'].sum())
        except:
            cap_comm_price_w_clicks = cap_comm_price

        cap_comm_price_periodo = (
            df.groupby('periodo')
            .apply(
                lambda group: (
                    (group['value'] * group['load']).sum() / group['load'].sum()
                ),
                include_groups=False
            )
        )
        cap_comm_price_periodo = self._map_periods(cap_comm_price_periodo)

        ap = ((df['value'] * df['load']).sum() / df['load'].sum()) / df['value'].mean()
        ap_periodo = df.groupby('periodo').apply(
            lambda row: (((row['value'] * row['load']).sum() / row['load'].sum()) / row['value'].mean()),
            include_groups=False
            )
        ap_periodo = self._map_periods(ap_periodo)

        cap_price_periodo = (
            df.groupby('periodo')
            .apply(
                lambda group: (
                    (group['coste_unitario'] * group['load']).sum() / group['load'].sum()
                ),
                include_groups=False
            )
        )
        cap_price_periodo = self._map_periods(cap_price_periodo)

        solar_profile = {
            "time": [f"{i}:00" for i in range(24)],  # Create hours 00:00, 01:00, ..., 23:00
            1: [0, 0, 0, 0, 0, 0, 0, 5, 15, 25, 40, 50, 50, 40, 25, 10, 5, 0, 0, 0, 0, 0, 0, 0],
            2: [0, 0, 0, 0, 0, 0, 0, 5, 15, 30, 55, 65, 65, 55, 40, 25, 15, 5, 0, 0, 0, 0, 0, 0],
            3: [0, 0, 0, 0, 0, 0, 5, 15, 30, 45, 60, 75, 85, 75, 60, 45, 30, 15, 5, 0, 0, 0, 0, 0],
            4: [0, 0, 0, 0, 0, 0, 10, 25, 45, 60, 75, 90, 100, 90, 75, 60, 45, 25, 10, 0, 0, 0, 0, 0],
            5: [0, 0, 0, 0, 0, 0, 15, 30, 50, 65, 85, 95, 100, 95, 85, 75, 65, 50, 30, 15, 0, 0, 0, 0],
            6: [0, 0, 0, 0, 0, 0, 20, 35, 60, 75, 90, 100, 100, 90, 75, 60, 50, 35, 25, 20, 0, 0, 0, 0],
            7: [0, 0, 0, 0, 0, 0, 10, 25, 45, 60, 75, 90, 100, 100, 95, 85, 70, 55, 35, 20, 5, 0, 0, 0],
            8: [0, 0, 0, 0, 0, 0, 15, 30, 50, 65, 85, 95, 100, 95, 85, 75, 65, 50, 30, 15, 0, 0, 0, 0],
            9: [0, 0, 0, 0, 0, 0, 10, 25, 45, 60, 75, 85, 90, 85, 75, 60, 45, 30, 15, 5, 0, 0, 0, 0],
            10: [0, 0, 0, 0, 0, 0, 5, 15, 30, 45, 60, 75, 85, 75, 60, 45, 30, 15, 5, 0, 0, 0, 0, 0],
            11: [0, 0, 0, 0, 0, 0, 0, 5, 15, 25, 40, 50, 55, 50, 40, 25, 15, 5, 0, 0, 0, 0, 0, 0],
            12: [0, 0, 0, 0, 0, 0, 0, 5, 15, 25, 40, 50, 50, 40, 25, 10, 5, 0, 0, 0, 0, 0, 0, 0]
        }

        df_solar_profile = pd.DataFrame(solar_profile)

        df_solar_profile = df_solar_profile.copy()

        df_solar_profile['time'] = pd.to_datetime(df_solar_profile['time'], format='%H:%M')

        df_solar_profile['time'] = df_solar_profile['time'].apply(lambda x: x.strftime('%H:%M'))
        df_solar_profile.set_index(df_solar_profile['time'], inplace=True)
        df_solar_profile.drop('time', axis=1, inplace=True)

        df['time'] = df['datetime'].dt.time.apply(lambda t: t.strftime('%H:%M'))
        df['month'] = df['datetime'].dt.month

        df['solar_load'] = df.apply(lambda row: df_solar_profile.loc[row['time'], row['month']], axis=1)

        df.drop(['time', 'month'], axis=1, inplace=True)

        solar_cost = (df['coste_unitario'] * df['solar_load']).sum() / df['solar_load'].sum()

        self.solar_avoided_price = solar_cost
        self.captured_commodity_price_periodo = cap_comm_price_periodo
        self.captured_commodity_price_total = cap_comm_price
        self.captured_commodity_price_w_clicks = cap_comm_price_w_clicks
        self.capture_rate_periodo = ap_periodo
        self.capture_rate_total = ap
        self.captured_price_h = price_captured_h
        self.captured_price_periodo = cap_price_periodo
        self.captured_price_total = (df['coste_unitario'] * df['load']).sum() / df['load'].sum()

    def _apply_formula(self, dict: dict):

         if self.contract_code in dict:
            # Call the corresponding method from the external dictionary
            return dict[self.contract_code](self)

    def _get_ap_fixed_percentage(self):

        df_cob = self.df_coberturas_fil.copy()

        def helper_click_period(row):
            if 'Q' in row['Producto']:
                return 'Ap_fixed_quarter'
            elif 'M' in row['Producto']:
                return 'Ap_fixed_month'
            elif 'YR' in row['Producto']:
                return 'Ap_fixed_yr'
            else:
                return 'Unknown'

        # Assign directly to the 'Ap' column
        if not df_cob.empty:
            df_cob['Ap'] = df_cob.apply(helper_click_period, axis=1)

            total_percentage = df_cob['Porcentaje [%]'].sum()

            perc_quarter = df_cob.loc[df_cob['Ap'] == 'Ap_fixed_quarter', 'Porcentaje [%]'].sum() / total_percentage
            perc_month = df_cob.loc[df_cob['Ap'] == 'Ap_fixed_month', 'Porcentaje [%]'].sum() / total_percentage
            perc_yr = df_cob.loc[df_cob['Ap'] == 'Ap_fixed_yr', 'Porcentaje [%]'].sum() / total_percentage
            print(perc_quarter)
            print(perc_month)
            print(perc_yr)

            df = self.df_verif.copy()
            df['Ap'] = (df['Ap_fixed_quarter'].fillna(0) * perc_quarter +
                        df['Ap_fixed_month'].fillna(0) * perc_month +
                        df['Ap_fixed_yr'].fillna(0) * perc_yr)

            self.df_coberturas_fil = df_cob
            self.df_verif = df


    def naturgy_1(self):
        '''
        Montfrisa 2023, 2024, Taghleef 2023 - 2026
        Tener en cuenta que la cobertura se liquida de forma física y en %

        '''
        df = self.df_verif.copy()
        captured_price = (df['value'] * df['load']).sum() / df['load'].sum()
        market_price = df['value'].mean()
        price_ratio = captured_price/market_price
        df['Ap'] = price_ratio

        if self.click:
            df['coste_unitario'] = \
            ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS']) * (1 + df['perd']) + df['Fee2']) * 1.015 + df['FNEE'] + df['ATR'])) \
            * (1 - df[self.click_columns[1]]) + \
            (((((df[self.click_columns[2]] + 0.2) * df['Ap'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS']) * (1 + df['perd']) + df['Fee2']) * 1.015 + df['FNEE'] + df['ATR'])) \
            * (df[self.click_columns[1]])

            # if df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum()) < df['Rango Inferior'].mean() * df['Cantidad [MWh]'].sum():

            #     penalty_load = df['Rango Inferior'] * df['Cantidad [MWh]'].sum() - df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum())
            #     penalty_cost = PENDIENTE

        else:
            df['coste_unitario'] = ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS']) * (1 + df['perd']) + df['Fee2'] + df['FNEE']) * 1.015 + df['ATR']))

        df['coste_total'] = df['coste_unitario'] * df['load'] / 1000

        self.df_verif = df
        return self 
    
    def cepsa_1(self):

        '''
        PR 2022-2023

        '''
        df = self.df_verif.copy()
        ds1 = df.groupby('periodo')[['value', 'load']].apply(lambda row: (row['value'] * row['load']).sum() / row['load'].sum())
        ponderated_total = (df['value'] * df['load']).sum() / df['load'].sum()
        ds = ds1/ponderated_total
        df_ap = pd.DataFrame(ds)
        df_ap.reset_index(inplace=True)
        df_ap.columns = ['periodo', 'Api']
        df = pd.merge(df, df_ap, how='left', left_on='periodo', right_on='periodo')

        if self.click:

            coste = \
            (df['value'] * (1 - df[self.click_columns[1]])) + (df[self.click_columns[2]] * df['Api']* df[self.click_columns[1]])
            df['coste_unitario'] = \
            ((((coste + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS']) * (1 + df['perd'])) + df['FNEE'] + df['Fee2'] * 1.015 + df['ATR']))

            # if df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum()) < df['Rango Inferior'].mean() * df['Cantidad [MWh]'].sum():

            #     penalty_load = df['Rango Inferior'] * df['Cantidad [MWh]'].sum() - df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum())
            #     penalty_cost = PENDIENTE

        else:
            df['coste_unitario'] = ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS']) * (1 + df['perd']) + df['Fee2'] + df['FNEE']) * 1.015 + df['ATR']))

        df['coste_total'] = df['coste_unitario'] * df['load'] / 1000
        df['coste_total'].sum()

        self.df_verif = df

        return self 

    def cepsa_2(self):

        '''
        PR 2024-2025

        '''
        df = self.df_verif.copy()
        ds1 = df.groupby('periodo')[['value', 'load']].apply(lambda row: (row['value'] * row['load']).sum() / row['load'].sum())
        ponderated_total = (df['value'] * df['load']).sum() / df['load'].sum()
        ds = ds1/ponderated_total
        df_ap = pd.DataFrame(ds)
        df_ap.reset_index(inplace=True)
        df_ap.columns = ['periodo', 'Api']
        df = pd.merge(df, df_ap, how='left', left_on='periodo', right_on='periodo')

        if self.click:

            print('hi')

            # ((df['value']) + (df[self.click_columns[2]] * df['Api']* df[self.click_columns[1]]))
            coste = \
            (df['value'] * (1 - df[self.click_columns[1]])) + (df[self.click_columns[2]] * df['Api']* df[self.click_columns[1]])
            df['coste_unitario'] = \
            ((((coste + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee2'] + df['FNEE']) * (1 + df['perd'])) * 1.015 + df['ATR']))

            # if df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum()) < df['Rango Inferior'].mean() * df['Cantidad [MWh]'].sum():

            #     penalty_load = df['Rango Inferior'] * df['Cantidad [MWh]'].sum() - df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum())
            #     penalty_cost = PENDIENTE

        else:
            df['coste_unitario'] = ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee2']) * (1 + df['perd']) + df['FNEE']) * 1.015 + df['ATR']))

        df['coste_total'] = df['coste_unitario'] * df['load'] / 1000
        df['coste_total'].sum()

        self.df_verif = df
        return self 
    
    def cepsa_3(self):

        '''
        PR 2024-2025

        '''
        df = self.df_verif.copy()
        ds1 = df.groupby('periodo')[['value', 'load']].apply(lambda row: (row['value'] * row['load']).sum() / row['load'].sum())
        ponderated_total = (df['value'] * df['load']).sum() / df['load'].sum()
        ds = ds1/ponderated_total
        df_ap = pd.DataFrame(ds)
        df_ap.reset_index(inplace=True)
        df_ap.columns = ['periodo', 'Api']
        df = pd.merge(df, df_ap, how='left', left_on='periodo', right_on='periodo')

        if self.click:

            print('hi')

            # (df['value'] * (1 - df[self.click_columns[1]])) + (df[self.click_columns[2]] * df['Api']* df[self.click_columns[1]])
            coste = \
            ((df['value']) + (df[self.click_columns[2]] * df['Api']* df[self.click_columns[1]]))
            df['coste_unitario'] = \
            ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee2'] + df['FNEE']) * (1 + df['perd'])) * 1.015 + df['ATR'])) \
            * (1 - df[self.click_columns[1]]) + \
            ((((df[self.click_columns[2]] * df['Api'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee2'] + df['FNEE']) * (1 + df['perd'])) * 1.015 + df['ATR'])) \
            * (df[self.click_columns[1]])

            # if df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum()) < df['Rango Inferior'].mean() * df['Cantidad [MWh]'].sum():

            #     penalty_load = df['Rango Inferior'] * df['Cantidad [MWh]'].sum() - df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum())
            #     penalty_cost = PENDIENTE

        else:
            df['coste_unitario'] = ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee2']) * (1 + df['perd']) + df['FNEE']) * 1.015 + df['ATR']))

        df['coste_total'] = df['coste_unitario'] * df['load'] / 1000
        df['coste_total'].sum()

        self.df_verif = df
        return self 

        # self.df_pass_through['coste_total'] = self.df_pass_through['']
    
    def endesa_1(self):

        df = self.df_verif.copy()

        if self.click:
            # ((df['B'] * df['value'].mean() + df['C'] + df['FNEE'])) \
            # ((df[self.click_columns[2]]  * df['B'] + df['C'] + df['FNEE'])) \
            df['coste_unitario'] = \
            ((df['B'] * df['value'].mean() + df['C'])) \
            * (1 - df[self.click_columns[1]]) + \
            ((df[self.click_columns[2]]  * df['B'] + df['C'])) \
            * (df[self.click_columns[1]])

        else:
            df['coste_unitario'] = ((df['B'] * df['value'].mean() + df['C'] + df['FNEE']))

        self.df_verif = df
        
        return self 
    
    def repsol_1(self):

        df = self.df_verif.copy()

        if self.click:
            df['coste_unitario'] = \
            ((df['B'] * df['value'] + df['A'])) * (1 - df[self.click_columns[1]]) + \
            ((df['B'] * df[self.click_columns[2]] + df['C'])) * (df[self.click_columns[1]])

        else:
            print('hi')
            df['coste_unitario'] = ((df['B'] * df['value'] + df['A']))
        
        # if df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum()) < df['Rango Inferior'].mean() * df['Cantidad [MWh]'].sum():

        #         penalty_load = df['Rango Inferior'] * df['Cantidad [MWh]'].sum() - df.apply(lambda row: (row['load'] * row['perc_cobertura']).sum())
        #         penalty_cost = PENDIENTE

        df['coste_total'] = df['coste_unitario'] * df['load'] / 1000
        self.df_verif = df
        
        return self 
    
    def total_1(self):

        '''
        Grupo Inspired, Kem One 2023

        '''
        self._get_ap_fixed_percentage()
        df = self.df_verif.copy()

        if self.click:
            df['coste_unitario'] = \
            ((((1.5 + df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1'] + df['FNEE']) * (1 + df['perd'])) * 1.015 + df['ATR'])) \
            * (1 - df[self.click_columns[1]]) + \
            ((((df[self.click_columns[2]] * df['Ap'] + 1.5 + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1'] + df['FNEE']) * (1 + df['perd'])) * 1.015 + df['ATR'])) \
            * (df[self.click_columns[1]])

        else:
            df['coste_unitario'] = ((((1.5 + df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1'] + df['FNEE']) * (1 + df['perd'])) * 1.015 + df['ATR']))

        self.df_verif = df
        return self 
    
    def total_2(self):
        '''
        Kem One 2024, 2025

        '''
        self._get_ap_fixed_percentage()
        df = self.df_verif.copy()

        if self.click:
            df['coste_unitario'] = \
            ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1']) * (1 + df['perd']) + df['FNEE']) * 1.015 + df['ATR'])) \
            * (1 - df[self.click_columns[1]]) + \
            ((((df[self.click_columns[2]] * df['Ap'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1']) * (1 + df['perd']) + df['FNEE']) * 1.015 + df['ATR'])) \
            * (df[self.click_columns[1]])

        else:
            df['coste_unitario'] = ((((df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1']) * (1 + df['perd']) + df['FNEE']) * 1.015 + df['ATR']))

        self.df_verif = df
        return self 
    
    def total_3(self):
        '''
        Kem One

        '''
        self._get_ap_fixed_percentage()
        df = self.df_verif.copy()

        if self.click:
            df['coste_unitario'] = \
            ((((1.5 + df['value'] + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1']) * (1 + df['perd']) + df['FNEE']) * 1.015)) \
            * (1 - df[self.click_columns[1]]) + \
            ((((df[self.click_columns[2]] * df['Ap'] + 1.5 + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1']) * (1 + df['perd']) + df['FNEE']) * 1.015)) \
            * (df[self.click_columns[1]])

        else:
            df['coste_unitario'] = ((((df['value'] + 1.5 + df['ssaa'] + df['PC'] + df['ROM'] + df['ROS'] + df['Fee1'] + df['Otros1']) * (1 + df['perd']) + df['FNEE']) * 1.015))

        self.df_verif = df
        self.coste_potencia = 0
        self.dto_electrointensivos_potencia = 0
        self.dto_electrointensivos = 0
        self.excesos_potencia = 0

        return self 
    
    def distribuidora(self):
        '''
        Kem One 2024, 2025

        '''
        df = self.df_verif.copy()

        df['coste_unitario'] = (df['ATR'])

        self.df_verif = df
        return self 