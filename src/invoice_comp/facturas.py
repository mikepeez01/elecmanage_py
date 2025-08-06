
import pandas as pd
import urllib3
import utils.utils_var as utils_var
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FacturasElec:

    def __init__(self, df: pd.DataFrame):

        self.facturas = df
        self.df_energia = pd.DataFrame()
        self.df_potencia = pd.DataFrame()
        self.df_maximetros = pd.DataFrame()

    def get_measurement(self, measure):

        df_measure = self.facturas[[
            'num_factura', 'month', 'cliente', 'alias', 'year',
                   f'{measure}_p1',
                   f'{measure}_p2',
                   f'{measure}_p3',
                   f'{measure}_p4',
                   f'{measure}_p5',
                   f'{measure}_p6']]
        measure_table = df_measure.groupby(['cliente', 'alias', 'month', 'year']).sum(numeric_only=True).reset_index()
        df_measure = pd.DataFrame(measure_table)
        df_measure = df_measure.sort_values(by=['cliente', 'alias', 'year', 'month'], ascending=[True, True, True, True])
        
        if measure == 'energia':
            df_measure['Total'] = df_measure.iloc[:, -6:].sum(axis=1)
            df_measure.iloc[:, -7:] = df_measure.iloc[:, -7:] / 1000
            self.df_energia = df_measure
        elif measure == 'potencia':
            self.df_potencia = df_measure
        elif measure == 'maximetros':
            self.df_maximetros = df_measure
        return df_measure, self

    def get_invoice_title(self):

        df_invoice = self.facturas[['cliente', 'alias', 'cups', 'num_factura', 'issue_date', 'year', 'month']]
        df_invoice.loc[:, 'issue_date'] = pd.to_datetime(df_invoice['issue_date']).dt.date
        df_last_invoice = df_invoice.loc[df_invoice.groupby(['cliente', 'alias', 'month', 'year'])['issue_date'].idxmax()]
        df_last_invoice = df_last_invoice.sort_values(by=['cliente', 'alias', 'year', 'month'], ascending=[True, True, True, True])
        df_last_invoice  = df_last_invoice.reset_index(drop=True)
        self.df_titles = df_last_invoice
        return df_last_invoice, self
    
    def get_invoices(self):

        df_invoice = self.facturas[['cliente', 'alias', 'cups',  'month', 'year',\
                                     'coste_energia', 'coste_reactiva', 'coste_potencia', 'excesos_potencia', 
                                     'dto_electrointensivo', 'total_bruto_ie_iva', 'total_bruto_iva']]
                                    
        grouped = df_invoice.groupby(['cliente', 'alias', 'month', 'year']).sum(numeric_only=True).reset_index()
        df_grouped = grouped.sort_values(by=['cliente', 'alias', 'year', 'month'], ascending=[True, True, True, True])
        self.df_invoices = df_grouped
        return df_grouped, self
    
    def set_period(self, attribute_name):

        df = getattr(self, attribute_name)

        try:
            df.loc[:, 'period'] = df.apply(lambda row:\
                                        f'{utils_var.map_month_name(row['month'])}-{str(row['year'])[-2:]}', axis=1)
            df = df.drop(['month', 'year'], axis=1)
            columns = df.columns.tolist()  # Get current columns as a list
            columns.insert(2, columns.pop(columns.index('period')))  # Move 'B' to third position
            df = df[columns]
            setattr(self, attribute_name, df)
        
        except KeyError: 
            print('hey')
            return self

    def group_facturas (self):

        # # Define columns for which you want the max
        # columns_for_max = [f'potencia_p{i}' for i in range (1,7)]  # Replace with actual column names

        # # Apply different aggregations: sum for numeric columns, max for selected ones
        # df = self.facturas.groupby(['cliente', 'alias', 'month', 'year'], as_index=False).agg(
        #     {col: 'max' for col in columns_for_max} | 
        #     {col: 'sum' for col in self.facturas.select_dtypes(include='number').columns if col not in columns_for_max}
        # )
        # df = self.facturas.groupby(['cliente', 'alias', 'year', 'month']).sum(numeric_only=True).reset_index()
        # df_grouped = df_grouped[self.facturas.columns[5:]]
        # df_grouped.set_index(['cliente', 'alias'], inplace=True)
        # df_grouped = df.sort_values(by=['cliente', 'alias', 'year', 'month'], ascending=[True, True, True, True])
        # df_grouped.reset_index(drop=False, inplace=True)
        # self.facturas = df_grouped

        df = self.facturas.groupby(['cliente', 'alias', 'month', 'year']).sum(numeric_only=True).reset_index()
        df_grouped = df.sort_values(by=['cliente', 'alias', 'year', 'month'], ascending=[True, True, True, True])
        self.facturas = df_grouped

    def update_column_names (self, attribute_name):

        df = getattr(self, attribute_name)

        if attribute_name == 'df_invoices':
            df = df.rename(columns={'period':'Periodo','coste_energia':'Coste Energía', 
                                    'coste_potencia':'Coste Potencia', 'coste_reactiva': 'Coste Reactiva', 
                                    'excesos_potencia':'Coste excesos',
                                    'dto_electrointensivo':'Descuento electrointensivos',
                                    'total_bruto_ie_iva': 'Base impuesto eléctrico',  
                                    'total_bruto_iva': 'Base imponible'})

        elif attribute_name == 'df_titles':
            df = df.rename(columns={'period':'Periodo', 'alias':'ALIAS', 'num_factura':'Num. Factura',
                                    'cups': 'CUPS', 'issue_date':'Fecha emisión'})
            
        else:
            for i in range (1, 7):
                pattern = f'p{i}'
                matching_columns = df.columns[df.columns.str.contains(pattern)]
                for col in matching_columns:
                    # New name for the column, you can define your own logic here
                    new_column_name = f'P{i}'
                    # Rename the column
                    df.rename(columns={col: new_column_name}, inplace=True)
            df = df.rename(columns={'period':'Periodo'})

        setattr(self, attribute_name, df)