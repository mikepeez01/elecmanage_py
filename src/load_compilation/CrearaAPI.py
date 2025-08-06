import pandas as pd
import requests
import xml.etree.ElementTree as ET
from enum import Enum
import datetime
import numpy as np



class CrearaAPI():

    class CategoryInventory(Enum):
        ENTITY = "entitats"
        CENTER = "centres_consum"
        SUPPLY = "subministraments"
        SOLAR_PLANT = "instalacions_solars"
        RECEIPTS = "factures"

        def __str__(self):
            return self.value

    class Resolution(Enum):
        TOTAL = "total"                # Un único resultado por el período analizado
        ANUAL = "anual"                # Resultados agrupados por años
        MONTHLY = "mensual"            # Resultados agrupados por meses
        DIARIO = "diari"               # Resultados agrupados por días
        HOURLY = "horari"             # Resultados agrupados por horas
        QUARTER_HOURLY = "quart-horari" # Resultados agrupados por 15 minutos
        FIVE_MINUTES = "cinc-min"     # Resultados agrupados por 5 minutos
        ONE_MINUTE = "un-min"           # Resultados agrupados cada minuto

        def __str__(self):
            return self.value

    class LoadColumnResolution(Enum):

        TOTAL = "total"                # Un único resultado por el período analizado
        ANUAL = "anual"                # Resultados agrupados por años
        MONTHLY = "mensual"            # Resultados agrupados por meses
        DIARIO = "daily"               # Resultados agrupados por días
        HOURLY = "hourly"             # Resultados agrupados por horas
        QUARTER_HOURLY = "quarter-hourly" # Resultados agrupados por 15 minutos
        FIVE_MINUTES = "five-minute"     # Resultados agrupados por 5 minutos
        ONE_MINUTE = "one-minute"

        def __str__(self):
            return self.value

    class Field(Enum):
        LOAD = "consum"             # Consumo de energía activa en kWh
        ACTIVE_POWER = "potencia_activa"  # Potencia activa en kW
        MAXIMETER = "potencia_maxima"  # Potencia máxima en kW
        REACTIVE = "reactiva"          # Consumo de energía reactiva en kVARh
        CO2 = "co2"                    # Toneladas equivalentes de CO2

        def __str__(self):
            return self.value
    
    class DataSource(Enum):
        INSTANTANEOUS = "instantanis"  # Medidas instantáneas del contador minuto a minuto
        COUNTER = "contador"           # Lectura de contador cada 15 minutos

        def __str__(self):
            return self.value

    def __init__(self, client_id, client_secret, grant_type):
        self.urlbase = 'https://api.gemweb.es'
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type

    def get_token(self):

        payload = f'request=get_token&client_id={self.client_id}&client_secret={self.client_secret}&grant_type={self.grant_type}'

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'oet=e5d01qqkgbiui79qso1us39ect'
        }
    
        response = requests.request("POST", self.urlbase, headers=headers, data=payload)

        if response.status_code == 200:

            root = ET.fromstring(response.content)

            for child in root:
                print(f"{child.tag}: {child.text}")
            
            access_token = root.find('access_token').text

            return access_token
            
        else:
            print(f"Request failed with status code {response.status_code}")
    
    def get_inventory(self, category: CategoryInventory):

        access_token = CrearaAPI.get_token(self)

        payload = f'request=get_inventory&access_token={access_token}&category={category}'

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'oet=e5d01qqkgbiui79qso1us39ect'
        }
    
        response = requests.request("POST", self.urlbase, headers=headers, data=payload)

        if response.status_code == 200:

            root = ET.fromstring(response.content)
            data = []
            for sub in root.findall('subministrament'):
                sub_data = {
                    'id': int(sub.find('id').text),
                    'id_entidad': int(sub.find('id_entitats').text),
                    'id_centro_consumo': int(sub.find('id_centres_consum').text),
                    'cups': sub.find('cups').text.strip(),
                    'tarifa': sub.find('tarifa_acces').text.strip(),
                }
                data.append(sub_data)

            print(root)

            return data
    
    def get_metering(self, 
                     id,
                     start_date: datetime.date,
                     end_date: datetime.date,
                     data_soruce: DataSource,
                     resolution: Resolution):
        
        access_token = CrearaAPI.get_token(self)

        payload = \
        f'request=get_metering&access_token={access_token}&id={id}&date_from={start_date}&date_to={end_date}&data_source={data_soruce}&period={resolution}'

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'oet=e5d01qqkgbiui79qso1us39ect'
        }
    
        response = requests.request("POST", self.urlbase, headers=headers, data=payload)

        if response.status_code == 200:

            root = ET.fromstring(response.content)
            data = []
            for value in root.findall(".//value"):
                date = value.get('date')
                try:
                    consumption = float(value.text)
                except:
                    consumption = np.nan
                data.append({"datetime": pd.to_datetime(date), "load": consumption})
            
            if data == None:
                df = pd.DataFrame()
            else:
                df = pd.DataFrame(data)
            return df
        else:
            print(response.status_code)
            return pd.DataFrame()