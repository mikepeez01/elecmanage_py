from verification_project.liquidation import Liquidation
# from verification_project.liquidation_copy import Liquidation as Liquidation
import load_compilation.load as load

cepsa_dict = {"WARNER3_C" : "ES0022000009138573BQ",
               "WARNER4_C" : "ES0022000009138572BS",
               "WARNER_C" : "ES0022000008103260DW",
               "VELERIN_C" : "ES0031102982960005WV",
               "TIVOLI_C" : "ES0031103666028002EF",
               "PR_OFI1_C" : "ES0021000012579474HN",
               "PR_OFI2_C" : "ES0021000012579469HF",
               "PR_OFI3_C" : "ES0021000012579468HY",
               "CULLERA_C" : "ES0021000007935634YX",
               "FAUNIA_C" : "ES0022000007945080PQ",
               "TRILLA_C" : "ES0022000007875397ST",
               "FAMESA_C" : "ES0031300149576005FE"
               }

provider_dict = {
    "cepsa" : (load.extract_cepsa, {"dict": cepsa_dict}),
    "creara" : (load.extract_creara, {}),  # No additional arguments
    "linkener" : (load.extract_linkener, {}),  # No additional arguments
    "seinon" : (load.extract_seinon, {}),  # No additional arguments
    "creara_quarter" : (load.extract_creara_quarter, {}),
    "taghleef_horaria_1" : (load.taghleef_horaria_1, {}),
    "taghleef_horaria_2" : (load.taghleef_horaria_2, {}),
    "clean" : (load.clean, {}),
    "total" : (load.extract_total, {}),
    "repsol_h" : (load.extract_repsol_h, {}),
    "repsol_combined" : (load.extract_repsol_h_q, {}),
    "iberdrola_distribuidora" : (load.extract_iberdrola_distr, {}),
    "seinon_pr2" : (load.seinon_pr2, {}),
}

contract_dict = {
    'Grupo Inspired_1_1': Liquidation.total_1,
    'Grupo Inspired_1_2': Liquidation.total_1,
    'Grupo Inspired_1_3': Liquidation.total_1,
    'Grupo Inspired_1_4': Liquidation.total_1,
    'Grupo Inspired_2_1': Liquidation.total_1,
    'Grupo Inspired_2_2': Liquidation.total_1,
    'Grupo Inspired_2_3': Liquidation.total_1,
    'Grupo Inspired_2_4': Liquidation.total_1,
    'Kem One_1_1' : Liquidation.total_3,
    'Kem One_1_2' : Liquidation.total_3,
    'Kem One_1_3' : Liquidation.total_3,
    'PR_1_1' : Liquidation.cepsa_1,
    'PR_1_2' : Liquidation.cepsa_2,
    'PR_1_3' : Liquidation.cepsa_2,
    'PR_2_1' : Liquidation.cepsa_1,
    'PR_2_2' : Liquidation.cepsa_2,
    'PR_2_3' : Liquidation.repsol_1,
    'PR_2_4' : Liquidation.repsol_1,
    'Taghleef_1_1': Liquidation.naturgy_1,
    'Taghleef_1_2': Liquidation.naturgy_1,
    'Taghleef_1_3': Liquidation.naturgy_1,
    'Taghleef_1_4': Liquidation.naturgy_1,
    'PR2_1_2' : Liquidation.endesa_1,
    'PR2_1_3' : Liquidation.endesa_1,
    'Generic_1_1' : Liquidation.total_1,
    'Generic_1_2' : Liquidation.total_1,
    'Generic_1_3' : Liquidation.total_1,
}

ver_mapping = {
    "cliente" : ("Ficha", "C7"),
    "alias" : ("Ficha", "C6"),
    "cups" : ("Ficha", "C8"),
    "tarifa" : ("Ficha", "C9"),
    "periodo" : ("Ficha", "C11"),
    "num_factura" : ("Ficha", "C12"),
    "consumo_fra" : ("Ficha", "B19"),               # Starting cell for 6-item list
    "energia_fra" : ("Ficha", "B38"),
    "potencia_fra" : ("Ficha", "B33"),
    "excesos_fra" : ("Ficha", "B34"),
    "reactiva_fra" : ("Ficha", "B51"),
    "dto_electrointensivos_fra" : ("Ficha", "B55"),
    "base_imponible_fra" : ("Ficha", "B58"),
    "potencia_contratada" : ("Ficha", "AA19"),       # Starting cell for 6-item list
    "consumo_ver" : ("Ficha", "F19"),
    "reactiva_ver" : ("Ficha", "B51"),
    "energia_ver" : ("Ficha", "F38"),
    "potencia_ver" : ("Ficha", "F33"),
    "excesos_ver" : ("Ficha", "F34"),
    "reactiva_ver" : ("Ficha", "F51"),
    "dto_electrointensivos_ver" : ("Ficha", "F55"),
    "base_imponible_ver" : ("Ficha", "F58")
    # "days" : ("Ficha", "AE17" ),
}

estim_mapping = {
    "alias" : ("Hoja1", "B5"),
    "cups" : ("Hoja1", "B7"),
    "periodo" : ("Hoja1", "C6"),
    "potencia_ver" : ("Hoja1", "C18"),
    "consumo_ver" : ("Hoja1", "C11"),
    "energia_ver" : ("Hoja1", "C22"),
    "excesos_ver" : ("Hoja1", "C19"),
    "dto_electrointensivos" : ("Hoja1", "C24"),
    "ie" : ("Hoja1", "C26"),
    "base_imponible_ver" : ("Hoja1", "C27")
    # "reactiva_ver" : ("Ficha", "F51"),
}