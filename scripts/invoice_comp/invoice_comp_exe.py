import papermill as pm
from config.config_loader import Config
from utils.logging_setup import start_new_log, get_logger, get_stream_writers
from pathlib import Path
from invoice_comp.invoice_comp_exe_helper import run_invoice_comp
import sys

config = Config()


# Paths
config_path = config.get_resolved_path("configs.config")
db_elec_path = config.get_path("data_path.elec.processed.facturas")
db_elec_manual_path = config.get_path("data_path.elec.processed.facturas_manual")
customers_path_single = config.get_resolved_path("data_path.elec.customers.folder")

# Notebook paths
nb_export = config.get_resolved_path("notebooks.invoice_comp.export")
nb_export_out = config.get_path("outputs.invoice_comp.notebooks.export")


run_invoice_comp("invoice_comp", config_path=config_path)

pm.execute_notebook(
    nb_export, nb_export_out,
    parameters=dict(
        config_path=config_path,
        db_elec_path=db_elec_path,
        db_elec_manual_path=db_elec_manual_path,
        customers_path_single=customers_path_single
    )
)
