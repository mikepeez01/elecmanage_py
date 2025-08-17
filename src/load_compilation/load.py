import pandas as pd
import xlrd
import os
from datetime import datetime,timedelta, time
import numpy as np
import json
from shared.elec_price_op import SpotElec
from utils.utils_var import set_datetime_h
from bs4 import BeautifulSoup
import logging

class Load:

    def __init__(self, 
                 periodos_path: str,
                 festivos_path:str,
                 base_path:str, 
                 load_path:str,
                 provider_dict: dict,
                 processed_files_path='processed_files.json'):

        self.periodos_path = periodos_path
        self.festivos_path = festivos_path
        self.base_path = base_path 
        self.provider_dict = provider_dict
        self.load_df = pd.DataFrame()
        self.load_path = load_path
        self.processed_files_path = processed_files_path
        self.processed_files = self._load_processed_files()
    
    def _load_processed_files(self):
        """
        Load the set of processed files from a JSON file.
        """
        if os.path.exists(self.processed_files_path):
            with open(self.processed_files_path, 'r') as f:
                return set(json.load(f))
        return set()

    def _save_processed_files(self):
        """
        Save the set of processed files to a JSON file.
        """
        with open(self.processed_files_path, 'w') as f:
            json.dump(list(self.processed_files), f)
        
    def compile_all_providers(self):
        """
        Compile load data for all providers in the base path.
        """
        for provider_name, (extract_func, func_args) in self.provider_dict.items():
            provider_path = os.path.join(self.base_path, provider_name)
            if not os.path.exists(provider_path):
                print(f"Warning: Provider folder '{provider_name}' does not exist. Skipping...")
                continue

            if provider_name == '.gitkeep':
                print(f"Skipping .gitkeep file in {provider_path}")
                continue

            logging.info(f"Processing provider: {provider_name}")
            files = os.listdir(provider_path)

            for file in files:
                file_path = os.path.join(provider_path, file)

                if file in self.processed_files:
                    print(f"  Skipping already processed file: {file}")
                    continue

                if file == '.gitkeep':
                    print(f"  Skipping .gitkeep file in {file}")
                    continue

                if os.path.isfile(file_path):
                    print(f"  Processing file: {file}")
                    df = extract_func(file_path, **func_args)

                    if 'resolution' not in df.columns:

                        if df['datetime'].dt.minute.nunique() == 1 and df['datetime'].dt.minute.unique()[0] == 0:
                                df['resolution'] = 'hourly'
                        elif set(df['datetime'].dt.minute.unique()).issubset({0, 15, 30, 45}):
                            df['resolution'] = 'quarter-hourly'
                        else:
                            df['resolution'] = 'unknown'

                    df['file'] = file
                    df['file_creation_time'] = os.stat(file_path).st_birthtime

                    df = df[['cups', 'datetime', 'resolution', 'load', 'file', 'file_creation_time']]

                    ApplyPeriodos = SpotElec(df)
                    ApplyPeriodos.format().apply_periodos(
                                                    periodos_path=self.periodos_path,
                                                    festivos_path=self.festivos_path
                                                    )
                    df_load_w_periodos = ApplyPeriodos.df_w_periodos.copy()
                    df_load_w_periodos = df_load_w_periodos[['cups', 'datetime', 'resolution', 'periodo', 'load', 'file', 'file_creation_time']]
                    df_load_w_periodos['file'] = df['file']
                    df_load_w_periodos['file_creation_time'] = df['file_creation_time']
                    self.load_df = pd.concat([self.load_df, df_load_w_periodos], ignore_index=True)

                    self.processed_files.add(file)
        
        self._save_processed_files()

    def save_to_parquet(self):
        """
        Save the compiled DataFrame to a Parquet file, ensuring that duplicates are handled
        properly using the `cumcount` method to distinguish between them.
        """

        if os.path.exists(self.load_path):
            df_existing_load = pd.read_parquet(self.load_path)
            rows_existing = df_existing_load.shape[0]
        else:
            df_existing_load = pd.DataFrame()
            rows_existing = 0

        if self.load_df.empty:
            print("No new load data to process.")
            return
        
        df = pd.concat([df_existing_load, self.load_df], ignore_index=True)

        df_load = remove_duplicates_with_exception(df)

        print(f"Rows replaced or added: {df_load.shape[0] - rows_existing}")

        df_load.to_parquet(self.load_path, engine='pyarrow', index=False)

        self.load_df = df_load

        print(f"Data successfully saved to {self.load_path}.")


def extract_cepsa (path, dict):

    workbook = xlrd.open_workbook(path)
    sheet = workbook['1']  

    cell_value = sheet.cell_value(rowx=1, colx=2)

    cups = dict[cell_value]

    df = pd.read_excel(path, sheet_name=1, skiprows=6)
    df = df.head(-4)
    df.dropna(axis=1, inplace=True)
    df['load'] = df[[f'PERIODO {i}' for i in range(1, 7)]].sum(axis=1)
    df = df[['FECHA', 'HORA', 'load']]

    df = df.groupby(['FECHA', 'HORA']).sum().reset_index()
    df = set_datetime_h('FECHA', 'HORA', 'load', df)
    df['cups'] = cups
    df['resolution'] = 'hourly'
    df.columns = ['datetime', 'load', 'cups', 'resolution']
    print(df.columns)

    df = df[['cups', 'datetime', 'resolution', 'load']]

    return df

def extract_creara(file_path):
    df_creara = pd.read_csv(file_path, sep=';')
    if len(df_creara.columns) == 2:
        df_creara['cups'] = df_creara.columns[1][-34:-14] 
        df_creara.columns = ['datetime', 'load', 'cups']
        df_creara = df_creara[['datetime', 'cups', 'load']]
    elif len(df_creara.columns) == 3:
        df_creara['cups'] = df_creara.columns[2][-37:-17] 
        df_creara.columns = ['datetime', 'none','load', 'cups']
        df_creara['load'] = df_creara.apply(lambda row: row['none'] if np.isnan(row['load']) else row['load'], axis=1)
        df_creara = df_creara[['datetime', 'cups', 'load']]
    df_creara['datetime'] = df_creara['datetime'].str.extract(r'(\d{2}/\d{2}/\d{4}) \[(\d{1,2}:\d{2})')[0] + " " + \
                    df_creara['datetime'].str.extract(r'(\d{2}/\d{2}/\d{4}) \[(\d{1,2}:\d{2})')[1]
    df_creara['datetime'] = pd.to_datetime(df_creara['datetime'], format='%d/%m/%Y %H:%M')

    return df_creara

def extract_creara_quarter(file_path):

    df = pd.read_csv(file_path, sep=';')
    df['cups'] = df.columns[1][:-6]
    df.columns = ['datetime', 'load', 'cups']
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df['resolution'] = 'quarter-hourly'
    df = df[['cups', 'datetime', 'resolution', 'load']]

    return df

def extract_linkener (file_path):

    df = pd.read_csv(file_path, sep=';')
    df = df.iloc[:, :3]
    df.columns = ['cups', 'datetime', 'load']
    df['datetime'] = pd.to_datetime(df['datetime'], dayfirst=True)
    df = df[['cups', 'datetime', 'load']]

    if df['datetime'].dt.minute.nunique() == 1 and df['datetime'].dt.minute.unique()[0] == 0:
        df['resolution'] = 'hourly'
        df['datetime'] = df['datetime'] - timedelta(hours=1)
    elif set(df['datetime'].dt.minute.unique()).issubset({0, 15, 30, 45}):
        df['resolution'] = 'quarter-hourly'
        df['datetime'] = df['datetime'] - timedelta(minutes=15)
    else:
        df['resolution'] = 'unknown'

    return df

def extract_seinon(file_path):
    """
    Custom function to process Seinon files.
    """
    df = pd.read_excel(file_path)
    df['datetime'] = pd.to_datetime(df['datetime'], dayfirst=True)
    df_c = df.copy()
    df_c['load'] = df_c['load'].replace('-', 0)
    # Example: Extract and process Seinon data
    return df_c

def extract_total(file_path):
    df = pd.read_csv(file_path, sep=';')
    cols = []
    for col in df.columns:
        if 'Activa' in col:
            cols.append(col)
    datetime = df['Category']
    df = df[cols]
    cols = []
    for col in df.columns:
        list = col.split(sep=' ')
        cups = list[1]
        try:
            num = int(cups[-3])
        except:
            cups = cups[:-2]
        cols.append(cups)
    df.columns = cols
    df['datetime'] = datetime

    month_map = {
        'ene.': 'jan.', 'feb.': 'feb.', 'mar.': 'mar.', 'abr.': 'apr.',
        'may.': 'may.', 'jun.': 'jun.', 'jul.': 'jul.', 'ago.': 'aug.',
        'sep.': 'sep.', 'oct.': 'oct.', 'nov.': 'nov.', 'dic.': 'dec.'
    }

    for spanish, english in month_map.items():
        df['datetime'] = df['datetime'].str.replace(spanish, english, regex=False)

    df['datetime'] = pd.to_datetime(df['datetime'], format='%d %b. %Y (%H:%M)', errors='coerce')
    df['datetime'] = df['datetime'] - timedelta(hours=1)
    df = pd.melt(
        df,
        id_vars=["datetime"],            # Columns to keep as is (datetime)
        var_name="cups",                 # Name for the new column containing original column names
        value_name="load"           # Name for the new column containing values
    )
    df.drop_duplicates(inplace=True)
    ds = df.groupby(['datetime', 'cups'])['load'].sum()
    df = pd.DataFrame(ds)
    df.reset_index(inplace=True)
    return df

def remove_duplicates_with_exception(df):
    """
    Remove duplicates from the DataFrame, but keep both rows for 2:00 AM on the
    last Sunday of October if their load values are identical.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing the data.

    Returns:
        pd.DataFrame: The deduplicated DataFrame.
    """
    from datetime import datetime, timedelta

    # Helper function to calculate the last Sunday of October
    def last_sunday_of_october(year):
        last_day = datetime(year, 10, 31)
        offset = (last_day.weekday() + 1) % 7
        return last_day - timedelta(days=offset)

    # Ensure datetime column is in datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Identify the year and last Sunday of October
    df['year'] = df['datetime'].dt.year
    df['last_sunday_oct'] = df['year'].apply(last_sunday_of_october)

    # Flag rows for 2:00 AM on the last Sunday of October
    df['is_2am_exception'] = (
        (df['datetime'].dt.date == df['last_sunday_oct'].dt.date) &
        (df['datetime'].dt.hour == 2)
    )

    # Separate 2:00 AM exception rows and others
    two_am_rows = df[df['is_2am_exception']]
    other_rows = df[~df['is_2am_exception']]

    # Handle duplicates for other rows (remove exact duplicates)
    other_rows = other_rows.sort_values(
        by='file_creation_time', 
        ascending=True
    )

    # Drop duplicates, keeping the most recent file_creation_time
    other_rows = other_rows.drop_duplicates(subset=['cups', 'datetime', 'resolution'], keep='last')

    # For 2:00 AM rows, keep both if load values are identical
    def handle_2am_duplicates(group):
            """
            Handles duplicate rows for the 2 a.m. exception on the last Sunday of October.

            If there is only one row, keep it. If there are multiple rows with the same datetime,
            keep up to two rows, prioritizing the most recent file_creation_time.
            """
            # Drop exact duplicates across all columns
            group = group.drop_duplicates()

            # If only one row, return it
            if len(group) == 1:
                return group

            # Sort by file_creation_time in descending order
            group = group.sort_values(by='file_creation_time', ascending=False)

            # Retain up to two most recent rows
            group = group.head(2)

            return group

    two_am_rows = two_am_rows.groupby(['cups', 'datetime']).apply(handle_2am_duplicates).reset_index(drop=True)


    # Combine the processed DataFrames
    result = pd.concat([other_rows, two_am_rows], ignore_index=True).reset_index(drop=True)

    # Clean up temporary columns
    result.drop(columns=['year', 'last_sunday_oct', 'is_2am_exception'], inplace=True)

    return result

def taghleef_horaria_1(file_path):

    df = pd.read_excel(file_path)
    df = df[['fecha', 'hora', 'medida']]
    df.columns = ['datetime', 'hora', 'load']
    df[df['hora'] == 25]
    df['cups'] = 'ES0031101457946001KR'
    df['datetime'] = pd.to_datetime(df['datetime'])

    df = set_datetime_h('datetime', 'hora', 'load', df)

    return df

def taghleef_horaria_2(file_path):

    df = pd.read_excel(file_path)

    df = df[['Fecha', 'Hora', 'Lectura']]
    df.columns = ['datetime', 'hora', 'load']
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d-%m-%Y')
    df['cups'] = 'ES0031101457946001KR'
    df = set_datetime_h('datetime', 'hora', 'load', df)
    df['load'] = df['load'].astype(str)
    df['load'] = df['load'].str.replace(',', '.', regex=False)
    df['load'] = df['load'].astype(float)

    return df

def clean(file_path):

    df = pd.read_pickle(file_path)
    
    return df

def extract_repsol_h (path):

    df = pd.read_excel(path)
    cups = df.columns[1][-22:-2]
    df.columns = df.iloc[2,:]
    df = df.iloc[3:,:]
    df.dropna(axis=1, inplace=True)
    print(f"Número de medidas estimadas: {df[df['Estimado/Real'] == 'E'].shape[0]}")
    df = df.iloc[:, :3]
    df['Hora'] = df['Hora'].astype(int)
    df['cups'] = cups
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
    df = set_datetime_h(
        hour='Hora',
        date='Fecha',
        load= df.columns[2],
        df=df
        )
    
    return df

def extract_repsol_h_q (path):

    df_quarter = pd.read_excel(path)
    cups = df_quarter.columns[1][-22:-2]
    df_quarter.columns = df_quarter.iloc[2,:]
    df_quarter = df_quarter.iloc[3:,:]
    df_quarter.dropna(axis=1, inplace=True)
    print(f"Número de medidas estimadas: {df_quarter[df_quarter['Estimado/Real'] == 'E'].shape[0]}")
    df_quarter.columns = ['date', 'hour', 'load', 'periodo', 'potencia', 'e/r']
    df = df_quarter.iloc[:, :3]
    df_quarter['cups'] = cups

    df_quarter['date'] = pd.to_datetime(df_quarter['date'], format='%d/%m/%Y').dt.date
    df_quarter['hour'] = df_quarter['hour'].replace('24:00', '00:00')
    df_quarter['hour'] = pd.to_datetime(df_quarter['hour'], format='%H:%M')


    df_quarter['hour'] = df_quarter['hour'] - timedelta(minutes=15)
    df_quarter['hour'] = df_quarter['hour'].dt.time
    df_quarter['datetime'] = df_quarter.apply(lambda row: datetime.combine(row['date'], row['hour']), axis=1)

    df_h = df_quarter.copy()

    df_h['hour'] = df_h['hour'].apply(lambda t: time(t.hour, 0, t.second))
    df_h['datetime'] = df_h.apply(lambda row: datetime.combine(row['date'], row['hour']), axis=1)
    ds_h = df_h.groupby('datetime')['load'].sum()

    df_h = pd.DataFrame(ds_h)
    df_h.reset_index(inplace=True)
    df_h['cups'] = cups
    
    df_h['resolution'] = 'hourly'
    df_quarter['resolution'] = 'quarter-hourly'
    df_quarter = df_quarter[df_h.columns]

    df = pd.concat([df_h, df_quarter], ignore_index=True)

    return df

def extract_iberdrola_distr(path):

    df = pd.read_csv(path, sep=';')
    df.sort_values('FECHA-HORA', inplace=True)
    df = df[['CUPS', 'FECHA-HORA', 'CONSUMO kWh']]
    df.columns = ['cups', 'datetime', 'load']
    df['datetime'] = pd.to_datetime(df['datetime'], format='mixed', dayfirst=True)
    df['dup'] = df.groupby(['cups', 'datetime']).cumcount()
    df['cups'] = df['cups'].str[:20]
    df = df.groupby(['cups', 'datetime', 'dup']).sum().reset_index()
    df.drop('dup', axis=1, inplace=True)
    if df['datetime'].dt.minute.nunique() == 1 and df['datetime'].dt.minute.unique()[0] == 0:
            df['resolution'] = 'hourly'
            df['datetime'] = df['datetime'] - timedelta(hours=1)
    elif set(df['datetime'].dt.minute.unique()).issubset({0, 15, 30, 45}):
        df['resolution'] = 'quarter-hourly'
        df['datetime'] = df['datetime'] - timedelta(minutes=15)
    else:
        df['resolution'] = 'unknown'

    return df  

def seinon_pr2(file_path):  

    # Leer el archivo como texto plano (código que ya tienes funcionando)
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parsear con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraer datos de la tabla manualmente
    rows = []
    for tr in soup.find_all('tr')[1:]:  # Saltar header
        cells = tr.find_all(['td', 'th'])
        if len(cells) >= 2:
            fecha = cells[0].get_text(strip=True)
            carga = cells[1].get_text(strip=True)  # Mantiene formato original
            rows.append([fecha, carga])

    # Crear DataFrame manualmente
    df_raw = pd.DataFrame(rows, columns=['datetime', 'load'])

    df = df_raw.copy()

    df = df.head(-1)

    # =====================================================
    # PROCESAR FECHAS
    # =====================================================
    def add_time(s):
        s = str(s)
        return s if ' ' in s else s + ' 00:00:00'

    # Aplicar función para asegurar formato datetime completo
    df['datetime'] = df['datetime'].apply(add_time)

    # Convertir a datetime con dayfirst=True para formato dd/mm/yyyy
    df['datetime'] = pd.to_datetime(df['datetime'], dayfirst=True)
    df['hour'] = df['datetime'].dt.time
    df['date'] = df['datetime'].dt.date

    # =====================================================
    # PROCESAR NÚMEROS (formato español)
    # =====================================================
    # Limpiar y convertir la columna 'Carga' a float
    # 1. Quitar puntos que marcan miles
    # 2. Cambiar comas por puntos para decimales  
    # 3. Convertir a float

    df['load'] = (
        df['load']
        .str.replace('.', '', regex=False)      # Quitar separador de miles
        .str.replace(',', '.', regex=False)     # Cambiar coma decimal por punto
        .astype(float)                          # Convertir a float
    )

    df_quarter = df.copy()
    df_h = df.copy()

    df_h['hour'] = df_h['hour'].apply(lambda t: time(t.hour, 0, t.second))
    df_h['datetime'] = df_h.apply(lambda row: datetime.combine(row['date'], row['hour']), axis=1)
    ds_h = df_h.groupby('datetime')['load'].sum()

    df_h = pd.DataFrame(ds_h)
    df_h.reset_index(inplace=True)

    df_h['resolution'] = 'hourly'
    df_quarter['resolution'] = 'quarter-hourly'
    df_quarter = df_quarter[df_h.columns]

    cups = 'ES0021000021881819JF'  # CUPS de ejemplo, ajustar según sea necesario

    df_h['cups'] = cups
    df_quarter['cups'] = cups

    df = pd.concat([df_h, df_quarter], ignore_index=True)
    return df