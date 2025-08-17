import logging
from config.config_loader import Config

def logging_setup(log_name: str, config_path, overwrite=False):
    """
    Set up logging to both file and console with append/overwrite options.

    Parameters:
    - log_name (str): Logical name for the log (used by your config).
    - config_path (str): Path to the configuration file.
    - overwrite (bool): If True, overwrite the existing log file. If False, append to it.
    """
    config = Config(config_file=config_path)
    log_path = config.get_path("logs.exe", log_name=log_name)

    # Avoid duplicate handlers, especially in repeated calls/workflows
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    filemode = 'w' if overwrite else 'a'
    logging.basicConfig(
        filename=log_path,
        filemode=filemode,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Add console handler (for terminal output)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

# # Example usage:
# logging_setup('workflow.log', config_path='path/to/config.yaml', overwrite=False)
# logging.info('This log will be saved to file AND shown on terminal.')
