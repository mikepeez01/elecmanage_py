import sys
import invoice_comp.cepsa as cepsa
import invoice_comp.naturgy as naturgy
import invoice_comp.total as total
import invoice_comp.nexus as nexus
import xml.etree.ElementTree as ET

def data_extraction (factura_e):

    tree = ET.parse(factura_e)
    root = tree.getroot()

    utility = root.find(".//LegalEntity/CorporateName").text
    print(utility)

    if 'CEPSA' in utility:
        return cepsa.elec(root)
    if 'GAS NATURAL COMERCIALIZADORA' in utility:
        return naturgy.elec(root)
    if 'TOTALENERGIES' in utility:
        return total.elec(root) 
    
def extract_cups (factura_e):

    tree = ET.parse(factura_e)
    
    root = tree.getroot()

    utility = root.find(".//LegalEntity/CorporateName").text
    print(utility)

    if 'CEPSA' in utility:
        return cepsa.cups(root)
    if 'GAS NATURAL COMERCIALIZADORA' in utility:
        return naturgy.cups(root)
    if 'TOTALENERGIES' in utility:
        return total.cups(root) 

def extract_month_year (factura_e):

    tree = ET.parse(factura_e)
    root = tree.getroot()

    utility = root.find(".//LegalEntity/CorporateName").text

    if 'CEPSA' in utility:
        return cepsa.extract_month_year(root)
    if 'GAS NATURAL COMERCIALIZADORA' in utility:
        return naturgy.extract_month_year(root)
    if 'TOTALENERGIES' in utility:
        return total.extract_month_year(root) 

def extract_num_fra_elec (factura_e):

    tree = ET.parse(factura_e)
    root = tree.getroot()
    utility = root.find(".//LegalEntity/CorporateName").text

    if 'CEPSA' in utility:
        return cepsa.num_fra_elec(root)
    if 'GAS NATURAL COMERCIALIZADORA' in utility:
        return naturgy.num_fra_elec(root)
    if 'TOTALENERGIES' in utility:
        return total.num_fra_elec(root)