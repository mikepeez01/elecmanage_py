import pandas as pd
import os
from datetime import datetime
import requests
import zipfile
import shutil
import utils.utils_dates as utils_dates
from utils.utils_var import set_datetime_h

class Liquicomon:

    def __init__(self,start_date: datetime, end_date: datetime, extract_path: str):

        self.start_date = start_date
        self.end_date = end_date
        self.extract_path = extract_path
    

    #     # https://api.esios.ree.es/archives/8/download?date_type=publicacion&end_date=2025-03-14T23%3A59%3A59%2B00%3A00&locale=es&start_date=2025-03-11T00%3A00%3A00%2B00%3A00
    #     # https://api.esios.ree.es/archives/8/download?date_type=publicacion&end_date=2025-05-21T23%3A59%3A59%2B00%3A00&locale=es&start_date=2025-05-01T00%3A00%3A00%2B00%3A00

    #     zip_url = (
    #         f"https://api.esios.ree.es/archives/8/download"
    #         f"?date_type=publicacion"
    #         f"&end_date={self.end_date.strftime('%Y-%m-%dT%H:%M:%S+00:00')}"
    #         f"&locale=es"
    #         f"&start_date={self.start_date.strftime('%Y-%m-%dT%H:%M:%S+00:00')}"
    #     )
    #     response = requests.get(zip_url)
    #     print(response.status_code)

    #     # father_path = (os.path.dirname(self.extract_path))
    #     # print(father_path)

    #     with open(f'{self.extract_path}/raw.zip', 'wb') as file:
    #         file.write(response.content)

    #     with zipfile.ZipFile(f'{self.extract_path}/raw.zip', 'r') as zip_ref:
    #         zip_ref.extractall(self.extract_path)

    #     zip_list = os.listdir(f'{self.extract_path}')
    #     print(zip_list)

    #     for zip_file in zip_list:
    #         full_path = os.path.join(self.extract_path, zip_file)
    #         if zip_file.endswith('.zip'):  # Ensure it's a zip file
    #             with zipfile.ZipFile(full_path, 'r') as zip_ref:
    #                 zip_ref.extractall(f'{self.extract_path}/raw_data')
    #                 print(f'Extracted: {full_path}')
    #         else:
    #             print(f'Skipped non-zip file: {full_path}')
    #     for zip_file in zip_list:
    #         if zip_file != 'raw.zip':
    #             if zip_file.endswith('.zip'):  # Ensure it's a zip file
    #                 os.remove(f'{self.extract_path}/{zip_file}')

    #     raw_data_list = os.listdir(f'{self.extract_path}/raw_data')
    #     for i in raw_data_list:
    #         if 'C2_compodem' not in i or '.' in i:
    #             os.remove(f'{self.extract_path}/raw_data/{i}')
    #     # os.remove(f'{father_path}/raw.zip')

    def ssaa_month (self, year , month):

        df_concat = pd.DataFrame()

        date_range = utils_dates.month_date_range(year, month)

        for i in date_range:

            date = utils_dates.format_date(i)
            df = pd.read_csv(f'{self.extract_path}/raw_data/C2_compodem_{date}', sep=';', skiprows=2, header=None)
            df = df[(df[3] == 'NOCUR') &
                    ((df[2] == 'RT3') |
                    (df[2] == 'CT3') |
                    (df[2] == 'RT6') |
                    (df[2] == 'BS3') |
                    (df[2] == 'BALX') |
                    (df[2] == 'EXD') |
                    (df[2] == 'DSV') |
                    (df[2] == 'IN7') |
                    (df[2] == 'CFP') |
                    (df[2] == 'MAJ3') |
                    (df[2] == 'RAD3') |
                    (df[2] == 'RAD1')
                    )]
            ds = df.groupby([0,1]).sum()
            df1 = pd.DataFrame(ds)
            df1 = df1.drop([2,3], axis=1)
            df1 = df1.reset_index()
            df1[0] = pd.to_datetime(df1[0], format='%d/%m/%Y')
            if len(df1) == 25:
                df1['datetime'] = df1.apply(lambda row: datetime(
                                        row[0].year,    # Year from first column
                                        row[0].month,   # Month from first column
                                        row[0].day,     # Day from first column
                                        (int(row[1]) - 1 if int(row[1]) <= 3 else int(row[1]) - 2),  # Hour logic
                                        0),  # Minute (always 0)
                             axis=1)
            elif len(df1) == 23:

                df1['datetime'] = df1.apply(lambda row: datetime(
                                        row[0].year,    # Year from first column
                                        row[0].month,   # Month from first column
                                        row[0].day,     # Day from first column
                                        (int(row[1]) - 1 if int(row[1]) <= 2 else int(row[1])),  # Hour logic
                                        0),  # Minute (always 0)
                             axis=1)

            else:
                df1['datetime'] = df1.apply(lambda row: datetime(row[0].year, row[0].month, row[0].day, int(row[1]) - 1, 0), axis=1)
            df1 = df1.drop([0, 1], axis=1)
            df1 = df1[['datetime', 6]]
            df1.columns = ['datetime', 'ssaa']

            df_concat = pd.concat([df_concat,df1], ignore_index=True)

        self.df_ssaa_m = df_concat

        return self
        
    def ssaa (self):

        df_concat = pd.DataFrame()
        compodem_list = os.listdir(f'{self.extract_path}/raw_data')

        if compodem_list != []:

            for i in compodem_list:
                if 'C2' in i:
                    df = pd.read_csv(f'{self.extract_path}/raw_data/{i}', sep=';', skiprows=2, header=None)
                    df = df[(df[3] == 'NOCUR')]
                    ds = df.groupby([0,1]).sum()
                    df1 = pd.DataFrame(ds)
                    df1 = df1.drop([2,3], axis=1)
                    df1 = df1.reset_index()
                    df1[0] = pd.to_datetime(df1[0], format='%d/%m/%Y')
                    if len(df1) == 25:
                        df1['datetime'] = df1.apply(lambda row: datetime(
                                                row[0].year,    # Year from first column
                                                row[0].month,   # Month from first column
                                                row[0].day,     # Day from first column
                                                (int(row[1]) - 1 if int(row[1]) <= 3 else int(row[1]) - 2),  # Hour logic
                                                0),  # Minute (always 0)
                                    axis=1)
                    elif len(df1) == 23:
                        df1['datetime'] = df1.apply(lambda row: datetime(
                                                row[0].year,    # Year from first column
                                                row[0].month,   # Month from first column
                                                row[0].day,     # Day from first column
                                                (int(row[1]) - 1 if int(row[1]) <= 2 else int(row[1])),  # Hour logic
                                                0),  # Minute (always 0)
                                    axis=1)
                    else:
                        df1['datetime'] = df1.apply(lambda row: datetime(row[0].year, row[0].month, row[0].day, int(row[1]) - 1, 0), axis=1)

                    df1 = df1.drop([0, 1], axis=1)
                    df1 = df1[['datetime', 6]]
                    df1.columns = ['datetime', 'ssaa']

                df_concat = pd.concat([df_concat,df1], ignore_index=True)
            
                df_concat = df_concat.sort_values(by= 'datetime')
                df_concat = df_concat.reset_index(drop=True)

            df_concat.loc[:, 'month'] = df_concat['datetime'].apply(lambda x: x.month)
            df_concat.loc[:,'year'] = df_concat['datetime'].apply(lambda x: x.year)
            df_concat = df_concat[['datetime', 'month', 'year', 'ssaa']]

            self.df_ssaa = df_concat
    
    def ssaa_desgolsado (self):

            df_concat = pd.DataFrame()
            df_c_global = pd.DataFrame()
            df_final = pd.DataFrame()

            compodem_list = os.listdir(f'{self.extract_path}/raw_data')

            list_params = ['CFP', 'DSV', 'RT3', 'CT3', 'RT6', 'BS3', 'BALX', 'EXD', 'IN7', 'MAJ3', 'RAD3', 'RAD1']

            for i in compodem_list:
                    
                if 'C2' in i and 'compodem' in i:
                
                    df = pd.read_csv(f'{self.extract_path}/raw_data/{i}', sep=';', skiprows=2, header=None)

                    df = df[(df[3] == 'NOCUR') 
                        # &
                        # ((df[2] == 'RT3') |
                        # (df[2] == 'CT3') |
                        # (df[2] == 'RT6') |
                        # (df[2] == 'BS3') |
                        # (df[2] == 'BALX') |
                        # (df[2] == 'EXD') |
                        # (df[2] == 'DSV') |
                        # (df[2] == 'IN7') |
                        # (df[2] == 'CFP') |
                        # (df[2] == 'MAJ3') |
                        # (df[2] == 'RAD3') |
                        # (df[2] == 'RAD1')
                        # )
                    ]
                    

                    df_concat = pd.concat([df_concat,df], ignore_index=True)

            df_concat[1] = df_concat[1].astype(int)

            df_concat[0] = pd.to_datetime(df_concat[0], format='%d/%m/%Y')

            for param in list_params:

                df_param = df_concat[df_concat[2] == param]
                df_param = df_param[[0,1,6]]
                df_param.columns = [0,1,param]
                # print(df_param.shape[0])
                if df_c_global.empty:
                    df_c_global = df_param
                else:
                    df_c_global = pd.merge(df_c_global, df_param, how='left', on=[0,1])


            for param in list_params:

                df_param = df_c_global[[0, 1, param]]
                df_param.columns = [0,1,'value']
                # print(df_param.shape[0])
                # list = df_param.groupby(df_param[0]).count().reset_index()
                # print(list[1].unique())
                df_c = set_datetime_h(
                    date=0, 
                    hour=1, 
                    load='value', 
                    df=df_param
                    )
                df_c = df_c.copy()
                df_c['parameter'] = param
                # print(df_c)
                df_c = df_c[['datetime','parameter', 'value']]
                df_final = pd.concat([df_final, df_c], ignore_index=True)

            self.df_ssaa_dt = df_final

            return df_final