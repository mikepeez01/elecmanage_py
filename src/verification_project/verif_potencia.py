import pandas as pd
import openpyxl
import utils.utils_dates as utils_dates
import numpy as np

class Curve:

    def __init__(self,
                 year: int,
                 tarifa: str,
                 df_load: pd.DataFrame,
                 power: list,
                 path_coefs_exc: str):
        
        self.tarifa = tarifa
        self.year = year
        self.df_load = df_load
        self.power = power
        self.path_coefs_exc = path_coefs_exc
        self.periods = [1,2,3,4,5,6]

    def read_coefs(self):

        df_tep = pd.read_excel(self.path_coefs_exc, sheet_name=str(self.year),skiprows=1, nrows=6)
        df_tep = df_tep[df_tep['Periodo'] == self.tarifa]
        df_tep.drop('Periodo', axis=1, inplace=True)
        df_tep.columns = self.periods
        df_tep = df_tep.T
        df_tep.columns = ['df_tep']
        self.df_tep = df_tep

        df_tep.columns = ['df_kp']
        df_kp = pd.read_excel(self.path_coefs_exc, sheet_name=str(self.year),skiprows=9, nrows=6)
        df_kp = df_kp[df_kp['Periodo'] == self.tarifa]
        df_kp.drop('Periodo', axis=1, inplace=True)
        df_kp.columns = self.periods
        df_kp = df_kp.T
        df_kp.columns = ['df_kp']
        self.df_kp = df_kp
    
        return self
    
    def map_power(self):

        df_pw = self.df_load.copy()

        df_pw['power'] = df_pw.apply(lambda row: self.power[row['periodo'] - 1], axis=1)
        df_pw['input'] = df_pw.apply(lambda row: (row['load'] - row['power']) ** 2 
                                if (row['load'] - row['power'] > 0) else 0, axis=1)
        self.df_pw = df_pw

        return self
    
    def calc_excesos(self):

        list_pw = self.df_pw.groupby('periodo')['input'].sum()

        pw_dict = list_pw.to_dict()

        mapped_pw = [pw_dict.get(period, 0) for period in self.periods]
        df_pw_grouped = pd.DataFrame(mapped_pw, index=self.periods, columns=['df_pw'])

        cost = np.sqrt(df_pw_grouped.iloc[:, 0]) * self.df_kp.iloc[:, 0] * self.df_tep.iloc[:, 0]
        self.cost = cost.sum()

        return self
        

