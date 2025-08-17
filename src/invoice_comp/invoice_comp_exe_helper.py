import papermill as pm
from config.config_loader import Config
from utils.logging_setup import logging_setup
import logging

def run_invoice_comp(project_name: str, config_path: str = None, log_name: str = 'invoice_comp') -> None:

    # Run the invoice compilation
    config = Config(config_file=config_path)
    logging_setup(log_name=log_name, config_path=config_path, overwrite=False)

    # Paths
    path_alias_elec = config.get_resolved_path("data_path.elec.customers.alias_elec")
    path_raw_data_elec = config.get_resolved_path("data_path.elec.invoice_comp.data_raw")
    path_fras_elec_xml_clean = config.get_resolved_path("data_path.elec.invoice_comp.xml_folder_clean")
    path_processed_files = config.get_path("data_path.elec.invoice_comp.processed_files")
    fras_folder = config.get_path("data_path.elec.invoice_comp.invoices.folder")
    invoice_sftp_config_path = config.get_resolved_path("configs.invoice_comp.sftp_params")
    db_elec_path = config.get_path("data_path.elec.processed.facturas")
    db_elec_manual_path = config.get_path("data_path.elec.processed.facturas_manual")

    # Notebook paths
    nb_arrange = config.get_resolved_path("notebooks.invoice_comp.arrange")
    nb_extract = config.get_resolved_path("notebooks.invoice_comp.extract")

    # Define the output paths for the workflow notebooks
    nb_arrange_out = config.get_path(f"outputs.{project_name}.notebooks.arrange")
    nb_extract_out = config.get_path(f"outputs.{project_name}.notebooks.extract")

    logging.info(f"Starting notebook for arranging invoice docs...")
    pm.execute_notebook(
        nb_arrange,  nb_arrange_out,
        parameters=dict(
            config_path=config_path,
            invoice_sftp_config_path=invoice_sftp_config_path,
            path_alias_elec=path_alias_elec,
            path_raw_data_elec=path_raw_data_elec,
            path_processed_files=path_processed_files,
            fras_folder=fras_folder,
            path_fras_elec_xml_clean=path_fras_elec_xml_clean,
        ),
        log_output=True
    )
    logging.info(f"Succesfully completed invoice arrangement workflow!\n")
    logging.info(f"Starting notebook for extracting invoice data...")
    pm.execute_notebook(
        nb_extract, nb_extract_out,
        parameters=dict(
            config_path=config_path,
            path_alias_elec=path_alias_elec,
            path_raw_data_elec=path_raw_data_elec,
            path_fras_elec_xml_clean=path_fras_elec_xml_clean,
            db_elec_path=db_elec_path,
            db_elec_manual_path=db_elec_manual_path
        ),
        log_output=True
    )
    logging.info(f"Succesfully completed invoice extraction workflow!")

    logging.info(f"Succesfully completed invoice_compilation workflow!")