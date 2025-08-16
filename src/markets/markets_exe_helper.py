import papermill as pm
from config.config_loader import Config
import yaml
from pathlib import Path
from utils.logging_setup import logging_setup
import logging

def market_data_retrieval(config_path, project, log_name):

    # Set up logging
    logging_setup(log_name=log_name, config_path=config_path, overwrite=False)

    config = Config(config_file=config_path)

    festivos_path = config.get_path("data_path.elec.regulation.festivos")
    periodos_cal_path = config.get_path("data_path.elec.regulation.calendario_periodos")
    futures_path = config.get_path("data_path.elec.processed.futures")
    spot_path = config.get_path("data_path.elec.processed.spot")
    spot_formated_path = config.get_path("data_path.elec.processed.spot_formatted")
    perd_path = config.get_path("data_path.elec.processed.perd_total")
    ssaa_path_c2 = config.get_path("data_path.elec.raw.ssaa", mode='c2')
    path_ssaa_c2_df = config.get_path("data_path.elec.processed.ssaa_df", mode='c2')
    path_ssaa_c2_df_dt = config.get_path("data_path.elec.processed.ssaa_df_detailed", mode='c2')

    path_markets_params = config.get_resolved_path("configs.markets.market_params")

    # Input notebooks
    nb_elec_markets_2a = config.get_path("notebooks.markets.elec_markets_2a")
    nb_elec_perd = config.get_resolved_path("notebooks.markets.perdidas")
    nb_elec_ssaa = config.get_resolved_path("notebooks.markets.ssaa")

    # Output notebooks
    nb_elec_markets_2a_out = config.get_path(f"outputs.{project}.notebooks.elec_markets_2a")
    nb_elec_perd_out = config.get_path(f"outputs.{project}.notebooks.perdidas")
    nb_elec_ssaa_out = config.get_path(f"outputs.{project}.notebooks.ssaa")

    with open(path_markets_params, 'r') as file:
        markets_params = yaml.safe_load(file)

    if markets_params['spot'] == True or markets_params['futures'] == True:
        logging.info(f"Descargando precios de electricidad (nb_elec_markets_2a)...")
        pm.execute_notebook(
            nb_elec_markets_2a, nb_elec_markets_2a_out,
            parameters=dict(
                config_path = config_path,
                log_name=log_name,
                festivos_path = festivos_path,
                periodos_cal_path = periodos_cal_path,
                futures_path = futures_path,
                spot_path = spot_path,
                spot_formated_path = spot_formated_path,
            ),
            log_output=True,

        )
        logging.info(f"Precios de electricidad descargados y procesados.")
    if markets_params['perd'] == True:

        pm.execute_notebook(
            nb_elec_perd, nb_elec_perd_out,
            parameters=dict(
                nb_name = Path(nb_elec_perd_out).stem,
                config_path = config_path,  
                perd_path = perd_path
            ),
            log_output=True
        )
    
    if markets_params['ssaa'] == True:
        pm.execute_notebook(
            nb_elec_ssaa, nb_elec_ssaa_out,
            parameters=dict(
                nb_name = Path(nb_elec_ssaa_out).stem,
                config_path = config_path,
                ssaa_path = ssaa_path_c2,
                ssaa_path_df = path_ssaa_c2_df,
                ssaa_path_df_dt = path_ssaa_c2_df_dt,
            ),
            log_output=True
        )