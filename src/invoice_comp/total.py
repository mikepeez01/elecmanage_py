import xml.etree.ElementTree as ET
from datetime import datetime
import invoice_comp.find_concepts as find_concepts

def elec (root):
    namespaces = {
        'utilities': 'http://www.facturae.es/Facturae/Extensions/Utilities'
    }

    taxable_base = float(root.find(".//InvoiceTotals/TotalGrossAmountBeforeTaxes").text)

    start_date = root.find(".//InvoicingPeriod/StartDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()

    end_date = root.find(".//InvoicingPeriod/EndDate")
    end_date = datetime.strptime(end_date.text, "%Y-%m-%d").date()

    issue_date = root.find(".//InvoiceIssueData/IssueDate")
    issue_date = datetime.strptime(issue_date.text, "%Y-%m-%d").date()
    #tarifa = root.find(".//UtilitiesAtrAsociado/TarifaDeAccesoATR") # no encuentro tarifa
    n_factura = root.find(".//InvoiceHeader/InvoiceNumber").text
    cups = root.find("Extensions/utilities:UtilitiesExtension/DatosDelSuministro/CUPS", namespaces).text

    try:
        number = int(cups[-3])
    except:
        cups = cups[:-2]

    potencia = find_concepts.find_invoice_line_period(line='P', 
                                                root=root.find("Extensions/utilities:UtilitiesExtension/DatosDelSuministro/PotenciasCaudales", namespaces),
                                                root_items='PotenciaCaudal',
                                                root_concept='Tipo',
                                                root_value='Valor')
    coste_potencia = find_concepts.find_invoice_line_period(line='Facturacion Potencia Periodo ', 
                                                root=root,
                                                root_items='InvoiceLine',
                                                root_concept='ItemDescription',
                                                root_value='TotalCost')

    energia = find_concepts.find_invoice_line_period(line='Consumo P', 
                                                root=root,
                                                root_items='InvoiceLine',
                                                root_concept='ItemDescription',
                                                root_value='Quantity')
    coste_energia = find_concepts.find_invoice_line_period(line='Consumo P', 
                                                root=root,
                                                root_items='InvoiceLine',
                                                root_concept='ItemDescription',
                                                root_value='TotalCost')

    maximetros = find_concepts.find_invoice_line_period(line='PM4', 
                                                root=root,
                                                root_items='DesgloseConsumos',
                                                root_concept='Tipo',
                                                root_value='ConsumoCalculado')
    
    cap_gas = find_concepts.find_invoice_line_single(
                                    line='CAP de gas', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    excesos_potencia = find_concepts.find_invoice_line_single(
                                    line='Termino Excesos Distribuidora', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    coste_reactiva = find_concepts.find_invoice_line_single(
                                    line='Termino Potencia Distribuidora', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    dto_elec_intensivo = find_concepts.find_invoice_line_single(
                                    line='ELECTROINTENSIV', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )
    
    ie = find_concepts.find_invoice_line_single(
                                    line='IMPUESTO SOBRE LA ELEC', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    if coste_reactiva is not None:
        coste_reactiva = float(coste_reactiva)
    else:
        coste_reactiva = 0

    if excesos_potencia is not None:
        excesos_potencia = float(excesos_potencia)
    else:
        excesos_potencia = 0

    if dto_elec_intensivo is not None:
        dto_elec_intensivo = float(dto_elec_intensivo)
    else:
        dto_elec_intensivo = 0

    taxable_base_total = taxable_base - ie
    coste_energia = taxable_base_total - sum(coste_potencia) - (excesos_potencia) - (coste_reactiva) + cap_gas

    print(f'Inicio periodo: {start_date}')
    print(f'Fin periodo: {end_date}')
    print(f'Fecha emision factura: {issue_date}')
    # print(tarifa.text)
    print(f'CUPS: {cups}\n')
    print(f'Potencia contratada por periodo:\n{potencia}\n')
    print(f'Energia consumida por periodo:\n{energia}\n')
    print(f'Coste potencia: {sum(coste_potencia)} €')
    print(f'Coste energia: {taxable_base_total - sum(coste_potencia) - float(excesos_potencia) - float(coste_reactiva)} €')
    print(f'Excesos de potencia: {excesos_potencia}')
    print(f'Descuento electrointensivos: {dto_elec_intensivo} €')
    print(f'Coste reactiva: {coste_reactiva} €')
    print(f'Total bruto (sin I.E ni IVA)  de potencia: {taxable_base_total} €')
    print(f'Base imponible (sin IVA): {taxable_base} €')

    dict_factura = {
        'num_factura': n_factura,
        'inicio_periodo': start_date,
        'fin_periodo': end_date,
        'issue_date': issue_date,
        'cups': cups,
        'potencia': potencia,
        'coste_potencia': sum(coste_potencia),
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

    namespaces = {
        'utilities': 'http://www.facturae.es/Facturae/Extensions/Utilities'
    }
    cups = root.find("Extensions/utilities:UtilitiesExtension/DatosDelSuministro/CUPS", namespaces).text
    try:
        return str(cups[:20])
    except:
        return None
    
def num_fra_elec (root):
    try: 
        return root.find(".//InvoiceHeader/InvoiceNumber").text
    except:
        return None
    
def extract_month_year (root):
    start_date = root.find(".//InvoiceIssueData/IssueDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()
    return start_date.month, start_date.year