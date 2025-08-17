import time

start = time.time()

import papermill as pm
import pandas as pd
import utils.utils_var as utils_var
from config.config_loader import Config
from load_compilation.load_compilation_exe_helper import run_load_compilation
import yaml
from invoice_comp.invoice_comp_exe_helper import run_invoice_comp
from pathlib import Path
import sys
from markets.markets_exe_helper import market_data_retrieval
from utils.logging_setup import logging_setup
import logging

config = Config()

config_path = config.get_resolved_path("configs.config")

festivos_path = config.get_path("data_path.elec.regulation.festivos")
periodos_cal_path = config.get_path("data_path.elec.regulation.calendario_periodos")

futures_path = config.get_path("data_path.elec.processed.futures")
spot_path = config.get_path("data_path.elec.processed.spot")
spot_formated_path = config.get_path("data_path.elec.processed.spot_formatted")

estado = 'C2'
perd_path = config.get_path("data_path.elec.processed.perd_total")

ssaa_path_c2 = config.get_path("data_path.elec.raw.ssaa", mode='c2')
path_ssaa_c2_df = config.get_path("data_path.elec.processed.ssaa_df", mode='c2')
path_ssaa_c2_df_dt = config.get_path("data_path.elec.processed.ssaa_df_detailed", mode='c2')
ssaa_path_a2 = config.get_path("data_path.elec.raw.ssaa", mode='a2')
path_ssaa_a2_df = config.get_path("data_path.elec.processed.ssaa_df", mode='a2')
path_ssaa_a2_df_dt = config.get_path("data_path.elec.processed.ssaa_df_detailed", mode='a2')

path_coefs_exc = config.get_path("data_path.elec.regulation.coefs_excesos")
path_ie = config.get_path("data_path.elec.regulation.ie")
path_ver_template = config.get_resolved_path("data_path.elec.verification_project.templates.verif")
path_estim_template = config.get_resolved_path("data_path.elec.verification_project.templates.estim")
compodem_a2_path = config.get_resolved_path("data_path.elec.verification_project.compodem_a2")

path_peajes_cargos_energia = config.get_resolved_path("data_path.elec.regulation.peajes_cargos_energia")
path_peajes_energia = config.get_resolved_path("data_path.elec.regulation.peajes_energia")
path_peajes_potencia = config.get_resolved_path("data_path.elec.regulation.peajes_potencia")
path_cargos_energia = config.get_resolved_path("data_path.elec.regulation.cargos_energia")
path_cargos_potencia = config.get_resolved_path("data_path.elec.regulation.cargos_potencia")
path_estructura_cargos = config.get_resolved_path("data_path.elec.regulation.estructura_cargos")
path_dto_peajes_electrointensivos = config.get_resolved_path("data_path.elec.regulation.dto_peajes_electrointensivos")

# Notebooks paths
nb_elec_prices = config.get_resolved_path("notebooks.markets.elec_markets_2a")
nb_elec_perd = config.get_resolved_path("notebooks.markets.perdidas")
nb_elec_ssaa = config.get_resolved_path("notebooks.markets.ssaa")
nb_load = config.get_resolved_path("notebooks.load_compilation.load_compile")

nb_elec = config.get_resolved_path("notebooks.verification_project.elec")
nb_market_matrix = config.get_resolved_path("notebooks.verification_project.build_matrix")
nb_market_matrix_estim = config.get_resolved_path("notebooks.verification_project.build_matrix_estim")
nb_contract_market_matrix = config.get_resolved_path("notebooks.verification_project.merge_market_contract")
nb_matrix_estim = config.get_resolved_path("notebooks.verification_project.build_matrix_estim")
nb_read_contracts = config.get_resolved_path("notebooks.verification_project.read_contract")
nb_estim = config.get_resolved_path("notebooks.verification_project.estimacion")
nb_invoices = config.get_resolved_path("notebooks.verification_project.hunt_invoices")
nb_verif = config.get_resolved_path("notebooks.verification_project.ver_nb")

# Output notebooks paths
nb_elec_prices_out = config.get_path("outputs.verification_project.notebooks.elec_markets_2a")
nb_elec_perd_out = config.get_path("outputs.verification_project.notebooks.perdidas")
nb_elec_ssaa_out = config.get_path("outputs.verification_project.notebooks.ssaa")
nb_load_out = config.get_path("outputs.verification_project.notebooks.load_compile")

nb_elec_out = config.get_path("outputs.verification_project.notebooks.elec")
nb_market_matrix_out = config.get_path("outputs.verification_project.notebooks.build_matrix")
nb_market_matrix_estim_out = config.get_path("outputs.verification_project.notebooks.build_matrix_estim")
nb_contract_market_matrix_out = config.get_path("outputs.verification_project.notebooks.merge_market_contract")
nb_matrix_estim_out = config.get_path("outputs.verification_project.notebooks.build_matrix_estim")
nb_read_contracts_out = config.get_path("outputs.verification_project.notebooks.read_contract")
nb_estim_out = config.get_path("outputs.verification_project.notebooks.estimacion")
nb_invoices_out = config.get_path("outputs.verification_project.notebooks.hunt_invoices")

db_elec_path = config.get_resolved_path("data_path.elec.processed.facturas")
db_elec_manual_path = config.get_resolved_path("data_path.elec.processed.facturas_manual")

path_load_parquet = config.get_path("data_path.elec.processed.load_parquet")

verification_params = config.get_resolved_path("configs.verification_project.verification_params")

# Carga el archivo de configuración
with open(verification_params, 'r') as file:
    params = yaml.safe_load(file)

# Acceso a los parámetros
cliente = params['cliente']
estim_year = params['estim_year']
estim_month = params['estim_month']
issue_year = params['issue_year']
issue_month = params['issue_month']
operation = params['operation']
update_contract_data = params['update_contract_data']
compile_load = params['compile_load']
compile_invoices = params['compile_invoices']
market_data = params['market_data']

path_alias_elec = config.get_resolved_path("data_path.elec.customers.alias_elec")
path_cliente_single = config.get_resolved_path("data_path.elec.customers.customer_single.folder", customer_id=cliente)
path_cliente_estim = config.get_path("outputs.verification_project.estim.cliente.folder", customer_id=cliente)

path_omie_matrix = config.get_path("data_path.elec.verification_project.omie_matrix", operation=operation)

# Explicitly start a fresh log for this run
instant = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
log_name=f"{operation} {cliente} {instant}",
logging_setup(
    log_name=log_name,
    config_path=config_path,
    overwrite=True
)

if operation == 'verif':
    logging.info(f"Starting {operation} run for customer {cliente} for {issue_year}-{issue_month}")
elif operation == 'estim':
    logging.info(f"Starting {operation} run for customer {cliente} for {estim_year}-{estim_month}")

# Descarga precios de electricidad
if market_data == True:
    market_data_retrieval(config_path=config_path, project="verification_project", log_name=log_name)

# Procesado curvas de carga
if compile_load == True:
    logging.info(f"Ejecutando flujo de trabajo load_compilation:\n")
    run_load_compilation('verification_project', config_path=config_path)
    logging.info(f"Load_compilation ejecutado {nb_load_out}")
else:
    logging.info(f"Skipping load compilation step as compile_load is set to False")

#### Incluir flujo de trabajo de invoice_comp
if compile_invoices == True:
    logging.info(f"Ejecutando flujo de trabajo invoice_comp:\n")
    run_invoice_comp('verification_project', config_path=config_path)
else:
    logging.info("Skipping invoice compilation step as compile_invoices is set to False")

# Construir matriz de mercado
logging.info(f"Ejecutando notebook:\n {nb_market_matrix}\n para la construcción de la matriz de mercado")
if operation == 'verif':
    pm.execute_notebook(
        nb_market_matrix, nb_market_matrix_out,
        parameters=dict(
            config_path = config_path,
            ssaa_path_df = path_ssaa_c2_df,
            perd_path = perd_path,
            spot_path = spot_path,
            spot_formated_path = spot_formated_path,
            futures_path = futures_path,
            path_omie_matrix = path_omie_matrix,
        ),
        log_output=True
    )
elif operation == 'estim':
    pm.execute_notebook(
        nb_market_matrix_estim, nb_market_matrix_estim_out,
        parameters=dict(
            config_path = config_path,
            year = estim_year,
            month = estim_month,
            ssaa_path_df = path_ssaa_a2_df,
            perd_path = perd_path,
            spot_path = spot_path,
            spot_formated_path = spot_formated_path,
            futures_path = futures_path,
            path_omie_matrix = path_omie_matrix,
            compodem_a2_path = compodem_a2_path,
        ),
        log_output=True
    )
logging.info(f"Notebook ejecutado y guardado en:\n {nb_market_matrix_out}")

# Ejecutar notebook maestro
logging.info(f"Ejecutando notebook:\n {nb_elec}\n para la verificación de contratos de electricidad")
pm.execute_notebook(
    nb_elec, nb_elec_out,
    parameters=dict(
        config_path = config_path,
        log_name = log_name,
        cliente = cliente,#
        estim_year = estim_year,
        estim_month = estim_month,
        issue_year = issue_year,
        issue_month = issue_month,
        operation = operation,
        update_contract_data = update_contract_data,
        path_alias_elec = path_alias_elec, #
        path_omie_matrix = path_omie_matrix,
        path_load_parquet = path_load_parquet,
        db_elec_path = db_elec_path,
        db_elec_manual_path = db_elec_manual_path,
        path_ver_template = path_ver_template,
        path_estim_template = path_estim_template,
        path_peajes_cargos_energia = path_peajes_cargos_energia,
        path_peajes_energia = path_peajes_energia,
        path_peajes_potencia = path_peajes_potencia,
        path_cargos_energia = path_cargos_energia,
        path_cargos_potencia = path_cargos_potencia,
        path_estructura_cargos = path_estructura_cargos,
        path_dto_peajes_electrointensivos = path_dto_peajes_electrointensivos,
        path_ie = path_ie,
        path_coefs_exc = path_coefs_exc,
        nb_read_contracts = nb_read_contracts,
        nb_read_contracts_out = nb_read_contracts_out,
        nb_contract_market_matrix = nb_contract_market_matrix,
        nb_contract_market_matrix_out = nb_contract_market_matrix_out,
        nb_invoices = nb_invoices,
        nb_invoices_out = nb_invoices_out,
        nb_estim = nb_estim,
        nb_estim_out = nb_estim_out,
        nb_verif = nb_verif,
    ),
    log_output=True
)
logging.info(f"Notebook ejecutado y guardado en:\n {nb_elec_out}")

end = time.time()

logging.info(f"Verification executed in {end - start:.2f} seconds")