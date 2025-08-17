from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pandas as pd

def obtener_trimestre(mes):  
    if 1 <= mes <= 3:
        return 1
    elif 4 <= mes <= 6:
        return 2
    elif 7 <= mes <= 9:
        return 3
    elif 10 <= mes <= 12:
        return 4
    else:
        return 0

def days_in_month(year, month):
    # Get the first day of the month
    first_day = datetime(year, month, 1)
    # Calculate the first day of the next month and subtract one day to get the last day of the current month
    last_day = first_day + relativedelta(months=1) - timedelta(days=1)
    return last_day.day

def map_month (es_date):   
    months_mapping = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12
    }

    return (months_mapping[es_date])

def map_month_name (num):

    months_mapping = {
        1: 'ene',
        2: 'feb',
        3: 'mar',
        4: 'abr',
        5: 'may',
        6: 'jun',
        7: 'jul',
        8: 'ago',
        9: 'sep',
        10: 'oct',
        11: 'nov',
        12: 'dic'
    }
    return (months_mapping[num])

def map_month_folder (num):

    months_mapping = {
        1: '01. Enero',
        2: '02. Febrero',
        3: '03. Marzo',
        4: '04. Abril',
        5: '05. Mayo',
        6: '06. Junio',
        7: '07. Julio',
        8: '08. Agosto',
        9: '09. Septiembre',
        10: '10. Octubre',
        11: '11. Noviembre',
        12: '12. Diciembre'
    }
    return (months_mapping[num])

def map_month_cap (num):

    months_mapping = {
        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE",
    }
    return (months_mapping[num])


def insert_alias (cups, df_alias):
    for index, row in df_alias.iterrows():
        if row['cups'] == cups:
            alias = row['alias']
            cliente = row['cliente']
            return [cliente, alias]
    print(f'No alias found for cups: "{cups}"')
    return [None, None]

import xlwings as xw

def export_excel_range_to_pdf(excel_path, pdf_path, sheet_name, cell_range):
    """
    Export a specific range of an Excel sheet to a PDF file on macOS.
    
    Args:
        excel_path (str): Path to the source Excel file.
        pdf_path (str): Path to save the exported PDF file.
        sheet_name (str): Name of the sheet containing the data.
        cell_range (str): Range of cells to export (e.g., "A1:D20").
    """
    # Open Excel application (visible=False for background operation)
    app = xw.App(visible=False)
    
    try:
        # Open workbook
        workbook = app.books.open(excel_path)
        sheet = workbook.sheets[sheet_name]
        
        # Set print area
        sheet.page_setup.print_area = cell_range
        
        # Export to PDF
        sheet.to_pdf(pdf_path)
        
        print(f"Exported range {cell_range} from {sheet_name} to {pdf_path}")
        
    finally:
        # Close workbook and quit Excel
        workbook.close()
        if not app.books:
            app.quit()

# Installation required: pip install xlwings


def set_datetime_h(date: str, hour: str, load: str, df):

    date_counts = df.groupby(date).size()

    dates_with_23_rows = date_counts[date_counts == 23].index
    condition_date_23_rows = df[date].isin(dates_with_23_rows)
    dates_with_25_rows = date_counts[date_counts == 25].index
    condition_date_25_rows = df[date].isin(dates_with_25_rows)
    dates_with_24_rows = date_counts[date_counts == 24].index
    condition_date_24_rows = df[date].isin(dates_with_24_rows)


    condition_hour_gte_1 = df[hour] < 3
    condition_hour_gte_2 = df[hour] >= 3

    df.loc[condition_date_23_rows & condition_hour_gte_1, date] = df.loc[condition_date_23_rows & condition_hour_gte_1].apply(
        lambda row: datetime(row[date].year, row[date].month, row[date].day, int(row[hour]) - 1),
        axis=1)

    df.loc[condition_date_23_rows & condition_hour_gte_2, date] = df.loc[condition_date_23_rows & condition_hour_gte_2].apply(
        lambda row: datetime(row[date].year, row[date].month, row[date].day, int(row[hour])),
        axis=1)

    condition_hour_gte_1 = df[hour] <= 3
    condition_hour_gte_2 = df[hour] > 3

    df.loc[condition_date_25_rows & condition_hour_gte_1, date] = df.loc[condition_date_25_rows & condition_hour_gte_1].apply(
        lambda row: datetime(row[date].year, row[date].month, row[date].day, int(row[hour]) - 1),
        axis=1)

    df.loc[condition_date_25_rows & condition_hour_gte_2, date] = df.loc[condition_date_25_rows & condition_hour_gte_2].apply(
        lambda row: datetime(row[date].year, row[date].month, row[date].day, int(row[hour]) - 2),
        axis=1)

    df.loc[condition_date_24_rows, date] = df.loc[condition_date_24_rows].apply(
        lambda row: datetime(row[date].year, row[date].month, row[date].day, int(row[hour]) - 1),
        axis=1)

    df.loc[:,date] = pd.to_datetime(df[date], errors='coerce')

    try: 
        df = df[['cups', date, load]]
        df.columns = ['cups', 'datetime', 'load']
    except:
        df = df[[date, load]]
        df.columns = ['datetime', 'value']

    return df

import pandas as pd
from datetime import datetime, timedelta

def set_datetime_h_adapted(day_of_year_col: str, hour_col: str, load_col: str, df: pd.DataFrame, year: int):
    """
    Adapts datetime handling for day-of-year format (1-365/366)
    
    Parameters:
    - day_of_year_col: Column name containing day of year (1-365/366)
    - hour_col: Column name containing hour (0-23)
    - load_col: Column name containing load/value data
    - df: DataFrame to process
    - year: Year to use for date conversion
    """
    
    # Convert day of year number to actual datetime date
    df['date_converted'] = df[day_of_year_col].apply(
        lambda x: datetime(year, 1, 1) + timedelta(days=int(x) - 1)
    )

    # Count occurrences per date to identify DST transitions
    date_counts = df.groupby('date_converted').size()

    # Identify special dates (DST transitions)
    dates_with_23_rows = date_counts[date_counts == 23].index  # Spring forward
    condition_date_23_rows = df['date_converted'].isin(dates_with_23_rows)
    
    dates_with_25_rows = date_counts[date_counts == 25].index  # Fall back
    condition_date_25_rows = df['date_converted'].isin(dates_with_25_rows)
    
    dates_with_24_rows = date_counts[date_counts == 24].index  # Normal days
    condition_date_24_rows = df['date_converted'].isin(dates_with_24_rows)

    # Handle 23-hour days (Spring DST transition)
    condition_hour_gte_1 = df[hour_col] < 3
    condition_hour_gte_2 = df[hour_col] >= 3

    df.loc[condition_date_23_rows & condition_hour_gte_1, 'date_converted'] = \
        df.loc[condition_date_23_rows & condition_hour_gte_1].apply(
            lambda row: datetime(
                row['date_converted'].year, 
                row['date_converted'].month, 
                row['date_converted'].day, 
                int(row[hour_col]) - 1
            ), axis=1
        )

    df.loc[condition_date_23_rows & condition_hour_gte_2, 'date_converted'] = \
        df.loc[condition_date_23_rows & condition_hour_gte_2].apply(
            lambda row: datetime(
                row['date_converted'].year, 
                row['date_converted'].month, 
                row['date_converted'].day, 
                int(row[hour_col])
            ), axis=1
        )

    # Handle 25-hour days (Fall DST transition)
    condition_hour_gte_1 = df[hour_col] <= 3
    condition_hour_gte_2 = df[hour_col] > 3

    df.loc[condition_date_25_rows & condition_hour_gte_1, 'date_converted'] = \
        df.loc[condition_date_25_rows & condition_hour_gte_1].apply(
            lambda row: datetime(
                row['date_converted'].year, 
                row['date_converted'].month, 
                row['date_converted'].day, 
                int(row[hour_col]) - 1
            ), axis=1
        )

    df.loc[condition_date_25_rows & condition_hour_gte_2, 'date_converted'] = \
        df.loc[condition_date_25_rows & condition_hour_gte_2].apply(
            lambda row: datetime(
                row['date_converted'].year, 
                row['date_converted'].month, 
                row['date_converted'].day, 
                int(row[hour_col]) - 2
            ), axis=1
        )

    # Handle normal 24-hour days
    df.loc[condition_date_24_rows, 'date_converted'] = \
        df.loc[condition_date_24_rows].apply(
            lambda row: datetime(
                row['date_converted'].year, 
                row['date_converted'].month, 
                row['date_converted'].day, 
                int(row[hour_col]) - 1
            ), axis=1
        )

    # Ensure datetime format
    df['date_converted'] = pd.to_datetime(df['date_converted'], errors='coerce')

    # Select and rename final columns
    try:
        df = df[['cups', 'date_converted', load_col]]
        df.columns = ['cups', 'datetime', 'load']
    except:
        df = df[['date_converted', load_col]]
        df.columns = ['datetime', 'value']

    return df
