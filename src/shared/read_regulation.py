import pandas as pd
from utils.utils_dates import days_in_year

class RegulationRetrievalHelper:

    def __init__(
            self, 
            tarifa: str,
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

        self.tarifa = tarifa
        self.path_peajes_cargos = path_peajes_cargos
        self.path_peajes_energia = path_peajes_energia
        self.path_cargos_energia = path_cargos_energia
        self.path_peajes_potencia = path_peajes_potencia
        self.path_cargos_potencia = path_cargos_potencia
        self.path_estructura_cargos = path_estructura_cargos
        self.path_ie = path_ie
        self.path_dto_peajes_electrointensivos = path_dto_peajes_electrointensivos
        self.path_coefs_exc = path_coefs_exc
        self.periods = [1,2,3,4,5,6]
        self.cargos_peajes_dict = {
            'peajes_energia' : self.path_peajes_energia,
            'cargos_energia' : self.path_cargos_energia,
            'peajes_potencia' : self.path_peajes_potencia,
            'cargos_potencia' : self.path_cargos_potencia
        }

    def _read_more_regulation(self, year: int):

        df_peajes_cargos = pd.read_excel(self.path_peajes_cargos, sheet_name=str(year), skiprows=3, na_filter=True)
        df  = df_peajes_cargos[(df_peajes_cargos.iloc[:, 0] == self.tarifa) | 
                            (df_peajes_cargos.iloc[:, 0].isin(['ROM', 'ROS', 'FNEE', 'Tasa']))]
        
        df.iloc[0,0] = 'PC'
        df.iloc[5,0] = 'ATR'
        df.columns = ['tarifa', 1, 2, 3, 4, 5, 6]
        df = df.reset_index(drop=True)
        df_tariffs = df.set_index('tarifa').T
        df_tariffs.columns.name = None
        df_tariffs.reset_index(inplace=True)
        df_tariffs.rename(columns={'index': 'periodo'}, inplace=True)
        return df_tariffs
    
    def _read_estructura_cargos(self, year: int):

        df = pd.read_excel(self.path_estructura_cargos, skiprows=1, na_filter=True)
        df = df[['Tipo', year]]
        df.columns = ['type', year]
        df = df.T

        df.columns = df.iloc[0] 
        df = df[1:] 

        return df
    
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

    def _read_ie(self):
        df = pd.read_excel(self.path_ie)
        self.df_ie = df
    
    def _read_dto_peajes_electrointensivos(self):
        df = pd.read_excel(self.path_dto_peajes_electrointensivos)
        self.df_dto_peajes_electrointensivos = df
    
    def _read_peajes_slash_cargos(self, parameter: str, year: int):

        if parameter not in self.cargos_peajes_dict:
            raise KeyError(f"Invalid parameter '{parameter}'. Expected one of {list(self.cargos_peajes_dict.keys())}.")

        path = self.cargos_peajes_dict[parameter]

        df = pd.read_excel(path, sheet_name=str(year), skiprows=1, na_filter=True)
        df.columns = ['tarifa', 1, 2, 3, 4, 5, 6]
        df = df.set_index('tarifa').T
        df.reset_index(drop=False, inplace=True)
        # df_tariffs.columns.name = None
        # df.reset_index(inplace=True)
        df.rename(columns={'index': 'periodo'}, inplace=True)
        df.index.name = None
        df = df[['periodo', self.tarifa]]
        df.columns = ['periodo', parameter]
        if 'potencia' in parameter:
            df[parameter] = df[parameter] / days_in_year(year)
            
        return df
    
    def _read_tep_power_exc_param(self, year):

        df_tep = pd.read_excel(self.path_coefs_exc, sheet_name=str(year),skiprows=1, nrows=6)
        df_tep = df_tep[df_tep['Periodo'] == self.tarifa]
        df_tep.drop('Periodo', axis=1, inplace=True)
        df_tep.columns = self.periods
        df_tep = df_tep.T
        df_tep.reset_index(inplace=True)
        df_tep.columns = ['periodo', 'tep_power_exc']

        return df_tep

    def _read_kp_power_exc_param(self, year):

        df_kp = pd.read_excel(self.path_coefs_exc, sheet_name=str(year),skiprows=9, nrows=6)
        df_kp = df_kp[df_kp['Periodo'] == self.tarifa]
        df_kp.drop('Periodo', axis=1, inplace=True)
        df_kp.columns = self.periods
        df_kp = df_kp.T
        df_kp.reset_index(inplace=True)
        df_kp.columns = ['periodo', 'kp_power_exc']
    
        return df_kp
    
    # def load_peajes_and_cargos_potencia(self):

    #     cargos_potencia = {}
    #     peajes_potencia = {}

    #     for year in self.years:
    #         cargos_potencia[year] = self._read_peajes_slash_cargos_potencia('cargos', year=year)
    #         peajes_potencia[year] = self._read_peajes_slash_cargos_potencia('peajes', year=year)

    #     with open(self.path_cargos_potencia_pkl, 'wb') as file:
    #         pickle.dump(peajes_potencia, file)
    #     with open(self.path_peajes_potencia_pkl, 'wb') as file:
    #         pickle.dump(cargos_potencia, file)