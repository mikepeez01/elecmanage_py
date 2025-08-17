from load_compilation.load_compilation_exe_helper import run_load_compilation
from config.config_loader import Config
from utils.logging_setup import logging_setup
import logging

config = Config()

config_path = config.get_resolved_path("configs.config")

log_name = 'load_compilation_exe'
logging_setup(log_name=log_name, config_path=config_path, overwrite=True)

run_load_compilation('load_compilation', config_path=config_path, log_name=log_name)