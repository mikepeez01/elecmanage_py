import pandas as pd
import openpyxl
import utils.utils_dates as utils_dates
import numpy as np
from datetime import timedelta, datetime, time

from shared.read_regulation import RegulationRetrievalHelper

class BuildMasterMatrix:

    def __init__(
            self, 
            cliente: str,
            cups: str,
            years: list, 
            tarifa: str,
            electrointensivo: bool,
            contract_id: int,
            path_datos_cliente: str, 
            path_peajes_cargos:str,
            path_peajes_energia: str,
            path_cargos_energia: str,
            path_peajes_potencia: str,
            path_cargos_potencia: str,
            path_estructura_cargos: str,
            path_ie:str,
            path_dto_peajes_electrointensivos: str,
            path_coefs_exc: str,
            ):

        self.cliente = cliente
        self.years = years
        self.cups = cups
        self.tarifa = tarifa
        self.electrointensivo = electrointensivo
        self.contract_id = contract_id
        self.path_datos_cliente = path_datos_cliente
        self.path_peajes_cargos = path_peajes_cargos
        self.path_peajes_energia = path_peajes_energia
        self.path_cargos_energia = path_cargos_energia
        self.path_peajes_potencia = path_peajes_potencia
        self.path_cargos_potencia = path_cargos_potencia
        self.path_estructura_cargos = path_estructura_cargos
        self.path_dto_peajes_electrointensivos = path_dto_peajes_electrointensivos
        self.path_ie = path_ie
        self.path_coefs_exc = path_coefs_exc
        self.periods = [1,2,3,4,5,6]

        datos_cliente = openpyxl.load_workbook(self.path_datos_cliente, data_only=True)
        self.contrato_marco = datos_cliente['Contrato Marco']

        self.RegulationRetrieval = RegulationRetrievalHelper(
            tarifa = self.tarifa,
            path_peajes_cargos = self.path_peajes_cargos,
            path_peajes_energia = self.path_peajes_energia,
            path_cargos_energia = self.path_cargos_energia,
            path_peajes_potencia = self.path_peajes_potencia,
            path_cargos_potencia = self.path_cargos_potencia,
            path_estructura_cargos = self.path_estructura_cargos,
            path_ie = self.path_ie,
            path_dto_peajes_electrointensivos = self.path_dto_peajes_electrointensivos,
            path_coefs_exc = self.path_coefs_exc
        )

    def trigger_master_df_completion(self, start_date, end_date):

        self.generate_contract_dataframe(start_date, end_date)
        self.insert_electrointensivo()
        self.insert_more_regulation()
        self.insert_estructura_cargos()
        self.insert_ie()
        self.insert_dto_peajes()

    def _preload_fees_data(self):
        """
        Load and preprocess the data from the Excel file.
        """
        # Load data once
        df_contrato = pd.read_excel(self.path_datos_cliente, sheet_name='Ficha Cliente', skiprows=20, nrows=6)
        
        # Clean and preprocess
        df_contrato = df_contrato.dropna(thresh=5, axis=1)
        df_contrato.set_index(df_contrato.columns[0], inplace=True)
        df_contrato.loc['contract_index'] = df_contrato.columns

        self.df_contrato = df_contrato

    def _read_electrointensivo(self):

        if self.electrointensivo == True:

            df_electrointensivo = pd.read_excel(self.path_datos_cliente, sheet_name='Electrointensivos')
        
            df_electrointensivo['start_date'] = pd.to_datetime(df_electrointensivo['start_date'])
            df_electrointensivo['end_date'] = pd.to_datetime(df_electrointensivo['end_date'])
            df_electrointensivo['start_date'] = df_electrointensivo['start_date'].apply(
                                                            lambda x: datetime.combine(x, time(0,0,0))
                                                        )
            df_electrointensivo['end_date'] = df_electrointensivo['end_date'].apply(
                                                        lambda x: datetime.combine(x, time(23,0,0))
                                                    )
            self.df_electrointensivo = df_electrointensivo
        else:
            self.df_electrointensivo = pd.DataFrame()
        
        return self

    def _get_cell_values(self, row, column):
        return [self.contrato_marco.cell(row=row, column=col).value for col in range(column + 1, column + 7)]

    def generate_contract_dataframe(self, start_date, end_date):
        """
        Generate a single DataFrame containing fees for all dates in the range.
        """
        self._preload_fees_data()
        pass_through_columns = ['Fee1', 'Otros1', 'Fee2', 'Otros2', 'Fee3', 'Otros3']
        pass_pool_columns = ['A', 'B', 'C', 'D']
        capture_rate_columns = ['Ap_fixed_yr',
            'Ap_fixed_quarter_1', 'Ap_fixed_quarter_2', 'Ap_fixed_quarter_3', 'Ap_fixed_quarter_4',
            'Ap_fixed_month_1', 'Ap_fixed_month_2', 'Ap_fixed_month_3', 'Ap_fixed_month_4',
            'Ap_fixed_month_5', 'Ap_fixed_month_6', 'Ap_fixed_month_7', 'Ap_fixed_month_8',
            'Ap_fixed_month_9', 'Ap_fixed_month_10', 'Ap_fixed_month_11', 'Ap_fixed_month_12'
                ]
        generic_capture_rate_columns = ['Ap_fixed_yr', 'Ap_fixed_quarter', 'Ap_fixed_month']

        fee_columns = \
            ['datetime', 'periodo', 'contract_index', 'utility', 'mode'] + \
                pass_through_columns + pass_pool_columns + capture_rate_columns
        
        final_columns = \
            ['cliente', 'cups', 'datetime', 'periodo', 'contract_id',\
            'contract_index', 'tarifa', 'utility', 'mode'] + \
                pass_through_columns + pass_pool_columns + generic_capture_rate_columns

        rows = []

        # Generate all unique dates
        unique_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        # Transpose and preprocess df_contrato for efficient lookups
        periods_df = self.df_contrato.T.reset_index()
        periods_df.rename(columns={
            'Fecha inicio': 'fecha_inicio',
            'Fecha fin': 'fecha_fin',
            'Comercializadora': 'utility',
            'Fórmula': 'mode'
        }, inplace=True)

        # Iterate over all dates
        for date in unique_dates:
            # Find the applicable period for the current date
            applicable_period = periods_df[
                (date >= periods_df['fecha_inicio']) &
                (date <= periods_df['fecha_fin'])
            ]

            if applicable_period.empty:
                # Skip dates with no applicable period
                continue

            # Retrieve utility and mode
            utility = applicable_period.iloc[0]['utility']
            utility_clean = utility.split(' ')[0]
            mode = applicable_period.iloc[0]['mode']
            contract_index = applicable_period.iloc[0]['contract_index']

            # Find the column index of the utility in contrato_marco
            column = next(cell.column for cell in self.contrato_marco[2] if cell.value == utility)

            # Mapping of column names to their corresponding row indices
            row_mapping = {
                'Fee1': 28, 'Otros1': 29,
                'Fee2': 30, 'Otros2': 31,
                'Fee3': 32, 'Otros3': 33,
                'A': 37, 'B': 38, 'C': 39, 'D': 40,
                'Ap_fixed_yr': 7,
                'Ap_fixed_quarter_1': 8, 'Ap_fixed_quarter_2': 9,
                'Ap_fixed_quarter_3': 10, 'Ap_fixed_quarter_4': 11,
                'Ap_fixed_month_1': 12, 'Ap_fixed_month_2': 13,
                'Ap_fixed_month_3': 14, 'Ap_fixed_month_4': 15,
                'Ap_fixed_month_5': 16, 'Ap_fixed_month_6': 17,
                'Ap_fixed_month_7': 18, 'Ap_fixed_month_8': 19,
                'Ap_fixed_month_9': 20, 'Ap_fixed_month_10': 21,
                'Ap_fixed_month_11': 22, 'Ap_fixed_month_12': 23,
            }

            # Pre-fetch all values using the mapping
            values = {key: self._get_cell_values(row, column) for key, row in row_mapping.items()}

            # Append rows for all periods
            for i in range(6):  # Assuming 6 periods
                rows.append({
                    'datetime': date,
                    'periodo': i + 1,
                    'contract_index': contract_index,
                    'utility': utility_clean,
                    'mode': mode,
                    **{key: values[key][i] for key in values}  # Dynamically add all mapped values
                })

        # Keep only the required columns
        master_df = pd.DataFrame(rows, columns=fee_columns)
        master_df = master_df.fillna(value=np.nan)
        master_df['datetime'] = pd.to_datetime(master_df['datetime'])
        master_df['month'] = master_df['datetime'].dt.month
        master_df['quarter'] = master_df['datetime'].apply(lambda x: utils_dates.obtener_trimestre(x.month))

        master_df['cliente'] = self.cliente
        master_df['cups'] = self.cups
        master_df['tarifa'] = self.tarifa 
        master_df['contract_id'] = self.contract_id

        master_df['Ap_fixed_month'] = master_df.apply(lambda row: row[f'Ap_fixed_month_{str(row['month'])}'], axis=1)
        master_df['Ap_fixed_quarter'] = master_df.apply(lambda row: row[f'Ap_fixed_quarter_{str(row['quarter'])}'], axis=1)
        master_df = master_df[final_columns]
        self.master_df = master_df

        return self

    def insert_ie(self):

        self.RegulationRetrieval._read_ie()  
        df_ie = self.RegulationRetrieval.df_ie
        master_df = self.master_df.copy()

        master_df['month'] = master_df['datetime'].dt.month
        master_df['year'] = master_df['datetime'].dt.year

        df_ie_melted = df_ie.melt(id_vars=['month'], var_name='year', value_name='ie')
        df_ie_melted['year'] = df_ie_melted['year'].astype(int)  # Ensure 'year' is numeric

        master_df = pd.merge(
            master_df,
            df_ie_melted,
            on=['month', 'year'],
            how='left'
        )
        
        master_df.drop(columns=['month', 'year'], inplace=True)
        self.master_df = master_df

        return self

    def insert_dto_peajes(self):

        master_df = self.master_df.copy()
        if 'electrointensivo' in master_df.columns:
            print(master_df['electrointensivo'].unique())
        self.RegulationRetrieval._read_dto_peajes_electrointensivos()  
        df_dto_peajes_electrointensivos = self.RegulationRetrieval.df_dto_peajes_electrointensivos

        master_df['month'] = master_df['datetime'].dt.month
        master_df['year'] = master_df['datetime'].dt.year

        df_dto_melted = df_dto_peajes_electrointensivos.melt(id_vars=['month'], var_name='year', value_name='dto_peajes')
        df_dto_melted['year'] = df_dto_melted['year'].astype(int)  # Ensure 'year' is numeric

        master_df = pd.merge(
            master_df,
            df_dto_melted,
            on=['month', 'year'],
            how='left'
        )
        
        master_df.drop(columns=['month', 'year'], inplace=True)
        # master_df['dto_peajes_energia'] = master_df['dto_peajes'] * (master_df['peajes_energia'])
        master_df['dto_peajes_energia'] = master_df.apply(
                                                    lambda row: 
                                                    row['dto_peajes'] * row['peajes_energia']
                                                    if row['electrointensivo'] else 0, axis=1
                                                    )
        master_df['dto_peajes_potencia'] = master_df.apply(
                                                    lambda row: 
                                                    row['dto_peajes'] * row['peajes_potencia']
                                                    if row['electrointensivo'] else 0, axis=1
                                                    )
        
        self.master_df = master_df

        return self
    
    def insert_electrointensivo(self):

        self._read_electrointensivo()
        master_df = self.master_df.copy()

        def insert_electro_helper(date_to_check,df):

            df['start_date'] = pd.to_datetime(df['start_date'], dayfirst=True, errors='coerce')
            df['end_date'] = pd.to_datetime(df['end_date'], dayfirst=True, errors='coerce')
            in_range = ((date_to_check >= df['start_date']) & (date_to_check <= df['end_date'])).any()
            return in_range

        if self.electrointensivo == True:

            master_df['electrointensivo'] = master_df['datetime'].apply(lambda date:
                                                            insert_electro_helper(
                                                                date, 
                                                                self.df_electrointensivo
                                                                            ))
        else:
            master_df['electrointensivo'] = False

        self.master_df = master_df

        return self
    
    def insert_estructura_cargos(self):

        estructura_cargos = {}
        master_df = self.master_df.copy()

        for year in self.years:

            estructura_cargos[year] = self.RegulationRetrieval._read_estructura_cargos(year)

        new_columns = master_df.apply(lambda row: self.assign_values_from_dict_year(row, estructura_cargos), axis=1)

        # Add the new columns to master_df
        master_df = pd.concat([master_df, pd.DataFrame(list(new_columns))], axis=1)

        self.master_df = master_df

        return self

    def insert_more_regulation(self):

        cargos_energia = {}
        peajes_energia = {}
        cargos_potencia = {}
        peajes_potencia = {}
        more_regulation = {}
        tep_power_exc_param = {}
        kp_power_exc_param = {}
        master_df = self.master_df.copy()

        for year in self.years:
            cargos_energia[year] = self.RegulationRetrieval._read_peajes_slash_cargos('cargos_energia', year)
            peajes_energia[year] = self.RegulationRetrieval._read_peajes_slash_cargos('peajes_energia', year)
            cargos_potencia[year] = self.RegulationRetrieval._read_peajes_slash_cargos('cargos_potencia', year)
            peajes_potencia[year] = self.RegulationRetrieval._read_peajes_slash_cargos('peajes_potencia', year)
            more_regulation[year] = self.RegulationRetrieval._read_more_regulation(year=year)
            tep_power_exc_param[year] = self.RegulationRetrieval._read_tep_power_exc_param(year=year)
            kp_power_exc_param[year] = self.RegulationRetrieval._read_kp_power_exc_param(year=year)
            # power_exc_parameters[year] = self.RegulationRetrieval._read

        # Using .apply() to assign cargos, peajes, and more_regulation
        for data_dict in [
            cargos_energia, peajes_energia,
            cargos_potencia, peajes_potencia,
            more_regulation,
            tep_power_exc_param, kp_power_exc_param
            ]:
            # Create a temporary DataFrame with the new values
            new_columns = master_df.apply(lambda row: self.assign_values_from_dict_periodo(row, data_dict), axis=1)
            # Add the new columns to master_df
            master_df = pd.concat([master_df, pd.DataFrame(list(new_columns))], axis=1)

        self.master_df = master_df

        return self
    
    def read_coberturas(self):

        df_coberturas = pd.read_excel(self.path_datos_cliente,sheet_name='Ficha Cliente', skiprows= 28, nrows=12)
        df_coberturas = df_coberturas.dropna(thresh=9, axis=1)  
        df_coberturas.set_index(df_coberturas.columns[0], inplace=True)
        df_coberturas.index.name = 'index'
        df_coberturas = df_coberturas.T
        # df_coberturas = df_coberturas[(df_coberturas['Año'] == year) &
        #                                 ((df_coberturas['Producto'] == ('Q' + str(utils_dates.obtener_trimestre(month)))) |
        #                                 (df_coberturas['Producto'] == ('M' + str(month))) |
        #                                 (df_coberturas['Producto'] == 'YR'))]
        return df_coberturas

    def assign_values_from_dict_periodo(self, row, data_dict):
        """
        Assign values from a yearly dictionary to a row based on its year and periodo.

        Args:
            row (pd.Series): A row from the DataFrame.
            data_dict (dict): A dictionary where keys are years and values are DataFrames.

        Returns:
            dict: A dictionary of column values for the row.
        """
        year = row['datetime'].year
        periodo = row['periodo']
        if year in data_dict:
            # Get the DataFrame for the year
            df = data_dict[year]
            # Check if the periodo exists in the year's DataFrame
            if periodo in df['periodo'].values:
                # Get the matching row from the year's DataFrame
                matching_row = df.loc[df['periodo'] == periodo]
                return {
                    col: matching_row[col].values[0]
                    for col in df.columns if col not in ['periodo']
                }
        # If no match, return NaN for the respective columns
        return {col: float('nan') for col in data_dict[next(iter(data_dict))].columns if col not in ['periodo']}
    
    def assign_values_from_dict_year(self, row, data_dict):
        """
        Assign values from a yearly dictionary to a row based on its year.

        Args:
            row (pd.Series): A row from the DataFrame.
            data_dict (dict): A dictionary where keys are years and values are DataFrames.

        Returns:
            dict: A dictionary of column values for the row.
        """
        year = row['datetime'].year
        if year in data_dict:
            # Get the DataFrame for the year
            df = data_dict[year]
            # Assume there's only one row in the DataFrame for the year
            matching_row = df.iloc[0]  # Get the first row
            return {
                col: matching_row[col]
                for col in df.columns  # Use DataFrame columns (not the index)
            }
        # If no match, return NaN for all columns
        return {col: float('nan') for col in data_dict[next(iter(data_dict))].columns}
    
