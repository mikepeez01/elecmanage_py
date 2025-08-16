import requests
import pandas as pd
from datetime import datetime

class EsiosAPI:

    def __init__(self, key, df_prices):

        self.key = key
        self.df_response = df_prices

    def get_raw_data(self, indicator: int, start_date:datetime, end_date: datetime):

        url = f'https://api.esios.ree.es/indicators/{indicator}?start_date={start_date}&end_date={end_date}&time_trunc=hour&geo_ids[]=3' #&time_agg=average

        headers = {
            "Content-type": "application/json",
            "Accept": "application/json; application/vnd.esios-api-v1+json",
            "x-api-key": self.key,
            #"Host": "api.esios.ree.es",
            #"Cookie": ""
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            df_response = pd.DataFrame(response.json())        
            df_response = pd.DataFrame(df_response.loc['values'].values[0])  
            df_response = df_response[['datetime', 'value']]
            df_response['datetime'] = df_response['datetime'].apply(lambda x: x[:-7])
            df_response['datetime'] = pd.to_datetime(df_response['datetime'])
        else:
            df_response = pd.DataFrame()
            print(f"Error {response.status_code}: {response.text}")

        self.df_response = df_response

        return self
        