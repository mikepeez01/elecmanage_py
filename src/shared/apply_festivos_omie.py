import pdfplumber
import pandas as pd
import io
import requests
import os
import utils.utils_dates as utils_dates
from datetime import datetime

def get_festivos_omie(year, path):

    pdf_url_1 = f'https://www.omie.es/sites/files/default/{year-1}-11/Calendario_{year}.PDF'
    pdf_url_2 = f'https://www.omie.es/sites/default/files/inline-files/{year-1}-11/Calendario_{year}.pdf'
    pdf_url_3 = f'https://www.omie.es/sites/default/files/inline-files/int_festivos_{year}_01_01_{year}_12_31.pdf'
    pdf_url_4 = f'https://www.omie.es/sites/default/files/{year-1}-11/Calendario_{year}_1.pdf'
    pdf_url_5 = f'https://www.omie.es/sites/default/files/inline-files/int_festivos_{year}_01_01_{year}_12_31_0.pdf'
    pdf_url_6 = f'https://www.omie.es/sites/default/files/{year}-11/int_festivos_{year}_01_01_{year}_12_31.pdf'
    pdf_url_7 = f'https://www.omie.es/sites/default/files/inline-files/calendario_{year}.pdf'
    pdf_url_8 = f'https://www.omie.es/sites/default/files/{year-1}-11/calendario_{year}.PDF'

    url_list = [pdf_url_1, pdf_url_2, pdf_url_3, pdf_url_4, pdf_url_5, pdf_url_6, pdf_url_7, pdf_url_8]

    for url in url_list:

        response = requests.get(url)
        
        if response.status_code == 200:

            print(url)
            pdf_file = io.BytesIO(response.content)
            
            with pdfplumber.open(pdf_file) as pdf:
                first_page = pdf.pages[0]  
                table = first_page.extract_table()

            df = pd.DataFrame(table[1:], columns=table[0])  
            df = df[df['Fiesta nacional'] == 'Sí']
            df.to_excel(f'{path}_{year}.xlsx', index= False)
            return 
        
    print(f"Failed to download PDF. Status code: {response.status_code}")
    return pd.DataFrame()
    
def apply_festivos (path):

    year = datetime.now().year
    years = years = list(range(2014, year+1))
    df_festivos = pd.DataFrame()
    # for i in [year -1, year]:
    for year in years:
        f_path = f'{path}_{year}.xlsx'
        if not os.path.exists(f_path):
            get_festivos_omie(year , path)
        df = pd.read_excel(f'{path}_{year}.xlsx')
        df['date'] = df['Fecha'].apply(lambda x: utils_dates.map_dates(x))
        df_festivos = pd.concat([df_festivos, df], ignore_index=True)

    return df_festivos
    