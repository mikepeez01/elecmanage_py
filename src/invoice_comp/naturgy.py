import xml.etree.ElementTree as ET
import sys
import invoice_comp.find_concepts as find_concepts
from datetime import datetime

def elec (root):

    start_date = root.find(".//InvoicingPeriod/StartDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()

    end_date = root.find(".//InvoicingPeriod/EndDate")
    end_date = datetime.strptime(end_date.text, "%Y-%m-%d").date()

    issue_date = root.find(".//InvoiceIssueData/IssueDate")
    issue_date = datetime.strptime(issue_date.text, "%Y-%m-%d").date()

    tarifa = root.find(".//UtilitiesAtrAsociado/TarifaDeAccesoATR").text # no encuentro tarifa
    n_factura = root.find(".//InvoiceHeader/InvoiceNumber").text
    nombre = root.find(".//AdministrativeCentre/Name").text
    cups = root.find(".//DatosDelSuministro/CUPS").text

    try:
        number = int(cups[-3])
    except:
        cups = cups[:-2]

    taxable_base = float(root.find(".//InvoiceTotals/TotalGrossAmount").text)

    potencia = find_concepts.find_invoice_line_period(
                                line='POTENCIA ACCESO P', 
                                root=root,
                                root_items='InvoiceLine',
                                root_concept='ItemDescription',
                                root_value='Quantity'
                                )
    coste_potencia_acceso = find_concepts.find_invoice_line_period(
                                    line='POTENCIA ACCESO P', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    coste_potencia_cargos = find_concepts.find_invoice_line_period(
                                    line='POTENCIA CARGOS P', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    energia = find_concepts.find_invoice_line_period(
                                line='ACTIVA CARGOS P', 
                                root=root,
                                root_items='InvoiceLine',
                                root_concept='ItemDescription',
                                root_value='Quantity')

    coste_energia = find_concepts.find_invoice_line_period(
                                    line='A ACTIVA P', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    coste_energia_acceso = find_concepts.find_invoice_line_period(
                                    line='A ACTIVA ACCESO P', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    
    coste_energia_cargos = find_concepts.find_invoice_line_period(
                                    line='A ACTIVA CARGOS P', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    fnee = find_concepts.find_invoice_line_single(
                                    line='FONDO DE EFICIENCIA ENERG', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    

    maximetros = find_concepts.find_invoice_line_period(
                                        line='MX P', 
                                        root=root,
                                        root_items='MedidaSobreEquipo',
                                        root_concept='Magnitud',
                                        root_value='ConsumoCalculado'
                                        )
    excesos_potencia = find_concepts.find_invoice_line_single(
                                    line='EXCESOS DE POTENCIA ACCESO', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    taxable_base_total = find_concepts.find_invoice_line_single(
                                    line='IMPUESTO ELÉCTRICO', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='Quantity'
                                    )

    coste_reactiva = find_concepts.find_invoice_line_single(
                                    line='REACTIVA', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    
    dto_elec_intensivo = find_concepts.find_invoice_line_single(
                                    line='ELECTROINTENS', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    
    alquiler_equipo_medida = find_concepts.find_invoice_line_single(
                                    line='ALQUILER', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    
    coste_potencia = sum(coste_potencia_acceso) + sum(coste_potencia_cargos)
    coste_energia = sum(coste_energia) + sum(coste_energia_acceso) + sum(coste_energia_cargos) + float(fnee)

    print(f'Inicio periodo: {start_date}')
    print(f'Fin periodo: {end_date}')
    print(f'Fecha emision factura: {issue_date}')
    # print(tarifa.text)
    print(f'CUPS: {cups}\n')
    print(f'Potencia contratada por periodo:\n{potencia}\n')
    print(f'Energia consumida por periodo:\n{energia}\n')
    print(f'Coste potencia: {(coste_potencia)} €')
    print(f'Coste energia: {coste_energia} €')
    print(f'Excesos de potencia: {excesos_potencia} €')
    print(f'Descuento electrointensivos: {dto_elec_intensivo} €')
    print(f'Coste reactiva: {coste_reactiva} €')
    print(f'Total bruto (sin I.E ni IVA): {taxable_base_total} €')
    print(f'Base imponible (sin IVA): {taxable_base} €')
    
    dict_factura = {
        'num_factura': n_factura,
        'inicio_periodo': start_date,
        'fin_periodo': end_date,
        'issue_date': issue_date,
        'cups': cups,
        'potencia': potencia,
        'coste_potencia': (coste_potencia),
        'energia': energia,
        'maximetros': maximetros,
        'coste_energia': coste_energia,
        'excesos_potencia': excesos_potencia,
        'dto_electrointensivo': dto_elec_intensivo,
        'coste_reactiva': coste_reactiva,
        'total_bruto_ie_iva': taxable_base_total,
        'total_bruto_iva': taxable_base
    }

    return dict_factura

def cups(root):
    try:
        return root.find(".//DatosDelSuministro/CUPS").text[:-2]
    except:
        return None
    
def extract_month_year (root):
    print('hi')
    start_date = root.find(".//InvoicingPeriod/StartDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()
    return start_date.month, start_date.year

def num_fra_elec (root):
    try: 
        return root.find(".//InvoiceHeader/InvoiceNumber").text
    except:
        return None