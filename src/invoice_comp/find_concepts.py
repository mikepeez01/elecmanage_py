import xml.etree.ElementTree as ET

def find_invoice_line_period(line, root, root_items, root_concept, root_value):
    list = [0] * 6
    for invoice_line in root.findall(f".//{root_items}"):
        item_description = invoice_line.find(f"{root_concept}").text
        for i in range (6):
            if f"{line}{i+1}" in item_description:#if all(word in item_description for word in f"{line}{i+1}".split()): 
                quantity = invoice_line.find(f"{root_value}").text
                if 'POTENCIA' in line:
                    list[i] = (float(quantity))
                else:
                    list[i] += (float(quantity))
    return list

def find_invoice_line_single(line, root, root_items, root_concept, root_value):
    quantity = 0
    for invoice_line in root.findall(f".//{root_items}"):
        item_description = invoice_line.find(f"{root_concept}").text
        if f"{line}" in item_description:
            quantity += float(invoice_line.find(f"{root_value}").text)
    try:
        return (quantity)
    except NameError:
        return 0

def find_first_invoice_value(root, root_items, root_concept, root_value):
    for invoice_line in root.findall(f".//{root_items}"):
        try:
            concept = invoice_line.find(f"{root_concept}").text
            value = float(invoice_line.find(f"{root_value}").text)
            return value  # Return on first valid match
        except (AttributeError, ValueError, TypeError):
            continue
    return 0  # If no valid match is found
