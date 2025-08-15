from load_compilation.load_compilation_exe_helper import run_load_compilation
from config.config_loader import Config

config = Config()

config_path = config.get_resolved_path("configs.config")

run_load_compilation('load_compilation', config_path=config_path)