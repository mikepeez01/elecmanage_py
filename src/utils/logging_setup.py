import logging
from config.config_loader import Config

def logging_setup(log_name: str, config_path, overwrite=False):
    """
    Set up logging with the option to append or overwrite log_file.

    Parameters:
    - log_file (str): Path to the log file.
    - overwrite (bool): If True, overwrite the existing log file. If False, append to it.
    """
    config = Config(config_file=config_path)
    log_path = config.get_path("logs.exe", log_name=log_name)

    filemode = 'w' if overwrite else 'a'  # 'w' = overwrite; 'a' = append
    logging.basicConfig(
        filename=log_path,
        filemode=filemode,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# # Example usage:
# # Overwrite the log:
# logging_setup('workflow.log', overwrite=True)
# logging.info('Started new log file.')

# # Append to log:
# logging_setup('workflow.log', overwrite=False)
# logging.info('Appended to existing log file.')
