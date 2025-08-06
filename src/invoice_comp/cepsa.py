import invoice_comp.find_concepts as find_concepts
from datetime import datetime

def elec (root):

    taxable_base = float(root.find(".//TaxableBase/TotalAmount").text)
    taxable_base_total = float(root.find(".//InvoiceTotals/TotalGrossAmount").text)
    
    start_date = root.find(".//InvoicingPeriod/StartDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()

    end_date = root.find(".//InvoicingPeriod/EndDate")
    end_date = datetime.strptime(end_date.text, "%Y-%m-%d").date()

    issue_date = root.find(".//InvoiceIssueData/IssueDate")
    issue_date = datetime.strptime(issue_date.text, "%Y-%m-%d").date()
    #tarifa = root.find(".//UtilitiesAtrAsociado/TarifaDeAccesoATR") # no encuentro tarifa
    n_factura = root.find(".//InvoiceHeader/InvoiceNumber").text
    nombre = root.find(".//AdministrativeCentre/Name").text
    cups = cups = root.find(".//AdditionalData/InvoiceAdditionalInformation").text

    try:
        number = int(cups[-3])
        cups = cups[6:]
    except:
        cups = cups[6:-2]

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

    
    coste_energia = taxable_base_total - sum(coste_potencia) - (excesos_potencia) - (coste_reactiva)

    print(f'Inicio periodo: {start_date}')
    print(f'Fin periodo: {end_date}')
    print(f'Fecha emision factura: {issue_date}')
    # print(tarifa.text)
    print(f'Nombre: {nombre}')
    print(f'CUPS: {cups}\n')
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
        'num_factura': n_factura,
        'inicio_periodo': start_date,
        'fin_periodo': end_date,
        'issue_date': issue_date,
        'cups': cups,
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

def cups(root):
    try:
        return root.find(".//AdditionalData/InvoiceAdditionalInformation").text[6:-2]
    except:
        return None

def extract_month_year (root):
    # start_date = root.find(".//InvoicingPeriod/StartDate")
    start_date = root.find(".//InvoiceIssueData/IssueDate")
    start_date = datetime.strptime(start_date.text, "%Y-%m-%d").date()
    return start_date.month, start_date.year

def num_fra_elec (root):
    try: 
        return root.find(".//InvoiceHeader/InvoiceNumber").text
    except:
        return None



