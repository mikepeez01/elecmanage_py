from config.config_loader import Config
from load_compilation.provider_notebook_executor import ProviderNotebookExecutor
import papermill as pm
from utils.logging_setup import logging_setup
import logging


def run_load_compilation(project_name="load_compilation", config_path=None, log_name="load_compilation_exe"):
    """
    Execute load compilation workflow for a specific project.
    
    Args:
        project_name (str): The project name to execute
    """
    # Initialize configuration
    config = Config(config_file=config_path)

    # Set up logging
    logging_setup(log_name=log_name, config_path=config_path, overwrite=False)
    
    # Define common paths
    common_paths = {
        'path_alias_elec': config.get_resolved_path("data_path.elec.customers.alias_elec"),
        'path_load_elec_folder': config.get_resolved_path("data_path.elec.load_compilation.folder"),
        'path_load_elec_clean': config.get_resolved_path("data_path.elec.load_compilation.provider", provider='clean'),
        'path_load_elec_linkener': config.get_resolved_path("data_path.elec.load_compilation.provider", provider='linkener'),
    }
    
    # Load processing notebook paths (using dynamic project)
    nb_load = config.get_resolved_path(f"notebooks.load_compilation.load_compile")
    nb_load_out = config.get_path(f"outputs.{project_name}.notebooks.load_compile")
    
    # Define extra paths for running nb_load
    path_load_parquet = config.get_path("data_path.elec.processed.load_parquet")
    path_load_elec_folder = config.get_resolved_path("data_path.elec.load_compilation.folder")
    processed_files_path = config.get_resolved_path("data_path.elec.load_compilation.processed_files")
    festivos_path = config.get_path("data_path.elec.regulation.festivos")
    periodos_cal_path = config.get_path("data_path.elec.regulation.calendario_periodos")
    
    # Get params path
    params_path = config.get_resolved_path(f"configs.load_compilation.provider_params")
    
    # Execute the workflow
    executor = ProviderNotebookExecutor(config, common_paths, project_name=project_name)
    executor.execute_workflow(params_path)
    
    # Execute load compilation notebook
    logging.info("Executing load compilation notebook...")
    pm.execute_notebook(
        nb_load, nb_load_out,
        parameters=dict(
            config_path=config_path,
            log_name=log_name,
            path_load_elec_folder=path_load_elec_folder,
            processed_files_path=processed_files_path,
            path_load_parquet=path_load_parquet,
            festivos_path=festivos_path,
            periodos_cal_path=periodos_cal_path,
        ),
        log_output=True
    )
    
    logging.info(f"Successfully completed load_compilation workflow!\n")