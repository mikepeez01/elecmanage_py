import xml.etree.ElementTree as ET
import sys
import invoice_comp.find_concepts as find_concepts
from datetime import datetime

def elec (factura_e):

    tree = ET.parse(factura_e)
    root = tree.getroot()

    taxable_base = float(root.find(".//TaxableBase/TotalAmount").text)
    taxable_base_total = float(root.find(".//InvoiceTotals/TotalGrossAmount").text)
    
    start_date = root.find(".//InvoicingPeriod/StartDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()

    end_date = root.find(".//InvoicingPeriod/EndDate")
    end_date = datetime.strptime(end_date.text, "%Y-%m-%d").date()

    issue_date = root.find(".//InvoiceIssueData/IssueDate")
    issue_date = datetime.strptime(issue_date.text, "%Y-%m-%d").date()
    #tarifa = root.find(".//UtilitiesAtrAsociado/TarifaDeAccesoATR") # no encuentro tarifa
    cups = root.find(".//AdditionalData/InvoiceAdditionalInformation")

    try:
        number = int(cups[-3])
    except:
        cups = cups[:-2]

    potencia = find_concepts.find_invoice_line_period(
                                line='POTENCIA ELECTRICA P', 
                                root=root,
                                root_items='InvoiceLine',
                                root_concept='ItemDescription',
                                root_value='Quantity'
                                )
    coste_potencia = find_concepts.find_invoice_line_period(
                                    line='POTENCIA ELECTRICA P', 
                                    root=root,
                                    root_items='InvoiceLine',
                                    root_concept='ItemDescription',
                                    root_value='TotalCost'
                                    )

    energia = find_concepts.find_invoice_line_period(
                                line='COSTE PEAJE VARIABLE P', 
                                root=root,
                                root_items='InvoiceLine',
                                root_concept='ItemDescription',
                                root_value='Quantity'
                                )
    # no encuentro maximetros
    excesos_potencia = find_concepts.find_invoice_line_single(
                                    line='EXCESO POTENCIA', 
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
    coste_reactiva = find_concepts.find_invoice_line_single(
                                line='REACTIVA', 
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
    
    coste_energia = taxable_base_total - sum(coste_potencia) - (excesos_potencia) - (coste_reactiva)

    print(f'Inicio periodo: {start_date}')
    print(f'Fin periodo: {end_date}')
    print(f'Fecha emision factura: {issue_date}')
    # print(tarifa.text)
    print(f'CUPS: {cups.text[6:-2]}\n')
    print(f'Potencia contratada por periodo:\n{potencia}\n')
    print(f'Energia consumida por periodo:\n{energia}\n')
    print(f'Coste potencia: {sum(coste_potencia)} €')
    print(f'Coste energia: {taxable_base_total - sum(coste_potencia) - float(excesos_potencia) - float(coste_reactiva)} €')
    print(f'Excesos de potencia: {excesos_potencia}')
    print(f'Descuento electrointensivos: {dto_elec_intensivo} €')
    print(f'Coste reactiva: {coste_reactiva}')
    print(f'Total bruto (sin I.E ni IVA)  de potencia: {taxable_base_total} €')
    print(f'Base imponible (sin IVA): {taxable_base} €')
    
    dict_factura = {
        'inicio_periodo': start_date,
        'fin_periodo': end_date,
        'issue_date': issue_date,
        'cups': cups.text[6:-2],
        'potencia': potencia,
        'coste_potencia': sum(coste_potencia),
        'energia': energia,
        'maximetros': [0]*6,
        'coste_energia': coste_energia,
        'excesos_potencia': excesos_potencia,
        'dto_electrointensivo': dto_elec_intensivo,
        'coste_reactiva': coste_reactiva,
        'total_bruto_ie_iva': taxable_base_total,
        'total_bruto_iva': taxable_base
    }

    return dict_factura


