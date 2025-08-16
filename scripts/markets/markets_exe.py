import papermill as pm
from config.config_loader import Config
from markets.markets_exe_helper import market_data_retrieval
from utils.logging_setup import logging_setup
import logging


config = Config()

config_path = config.get_resolved_path("configs.config")
nb_elec_markets_2b = config.get_path("notebooks.markets.elec_markets_2b")
nb_elec_markets_2b_out = config.get_path("outputs.markets.notebooks.elec_markets_2b")
futures_path = config.get_path("data_path.elec.processed.futures")
spot_path = config.get_path("data_path.elec.processed.spot")
spot_formated_path = config.get_path("data_path.elec.processed.spot_formatted")

# Set up logging
log_name = 'markets_exe'
logging_setup(log_name=log_name, config_path=config_path, overwrite=True)

market_data_retrieval(config_path=config_path, project="markets", log_name=log_name)

logging.info("Ejecutando notebook")
logging.info(f"{nb_elec_markets_2b}")
logging.info("Para analisis de precios spot de mercado")
pm.execute_notebook(
    nb_elec_markets_2b, nb_elec_markets_2b_out,
    parameters=dict(
        config_path=config_path,
        futures_path=futures_path,
        spot_path=spot_path,
        spot_formated_path=spot_formated_path
    )
)
