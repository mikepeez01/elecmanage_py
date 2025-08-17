import papermill as pm
from config.config_loader import Config
from pathlib import Path
from invoice_comp.invoice_comp_exe_helper import run_invoice_comp
import sys
from utils.logging_setup import logging_setup
import logging

config = Config()


# Paths
config_path = config.get_resolved_path("configs.config")
db_elec_path = config.get_path("data_path.elec.processed.facturas")
db_elec_manual_path = config.get_path("data_path.elec.processed.facturas_manual")
customers_path_single = config.get_resolved_path("data_path.elec.customers.folder")

# Notebook paths
nb_export = config.get_resolved_path("notebooks.invoice_comp.export")
nb_export_out = config.get_path("outputs.invoice_comp.notebooks.export")

project_name = "invoice_comp"
log_name = "invoice_comp_exe"
# Set up logging
logging_setup(log_name=log_name, config_path=config_path, overwrite=True)

################
run_invoice_comp(project_name=project_name, config_path=config_path, log_name=log_name)

pm.execute_notebook(
    nb_export, nb_export_out,
    parameters=dict(
        config_path=config_path,
        db_elec_path=db_elec_path,
        db_elec_manual_path=db_elec_manual_path,
        customers_path_single=customers_path_single
    ),
    log_output=True
)
