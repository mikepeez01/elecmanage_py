# logger_setup.py
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple
from config.config_loader import Config

LOGGER_NAME = "elecmanage"  # project-level named logger

def _build_log_path(config: Config, log_name: str) -> Path:
    # Your existing resolver; ensure it returns a real filesystem path
    # Example: config.get_path('logs.exe', log_name=log_name) -> str/Path
    p = config.get_path('logs.exe', log_name=log_name)
    return Path(p)

def configure_logging(log_name: str,
                      config: Config,
                      *,
                      new_run: bool = False,
                      console_level: int = logging.INFO,
                      file_level: int = logging.DEBUG,
                      propagate_to_root: bool = False) -> logging.Logger:
    """
    Configure the project logger and its handlers.

    - new_run=True: start a fresh log (truncate).
    - new_run=False: append to existing log.
    """
    log_path = _build_log_path(config, log_name)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter

    # Remove existing handlers only when reconfiguring here
    if logger.handlers:
        for h in list(logger.handlers):
            logger.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass

    # Decide file mode based on new_run
    file_mode = "w" if new_run else "a"

    # Handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)

    file_handler = logging.FileHandler(log_path, mode=file_mode, encoding="utf-8")
    file_handler.setLevel(file_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Attach
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Control propagation to root to prevent duplicate logs
    logger.propagate = propagate_to_root

    logger.debug(
        "Logging configured: file=%s mode=%s console_level=%s file_level=%s new_run=%s",
        str(log_path), file_mode, logging.getLevelName(console_level),
        logging.getLevelName(file_level), new_run
    )
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get the project logger (or a child).
    - get_logger() -> 'elecmanage'
    - get_logger('pipeline.step') -> 'elecmanage.pipeline.step'
    """
    if not name:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")

def start_new_log(log_name: str, config: Config) -> logging.Logger:
    """
    Convenience wrapper to explicitly start a new log.
    Call this in the activating/driver script at the beginning of a run.
    """
    return configure_logging(log_name, config, new_run=True)

class LoggerWriter:
    """
    A file-like object that forwards written lines to a logger at a given level.
    Use this to route Papermill's streamed stdout/stderr into your logger.
    """
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self._buffer = ""

    def write(self, message: str):
        # Accumulate and emit on newline to avoid partial messages
        if not isinstance(message, str):
            message = str(message)
        self._buffer += message
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if line:
                self.logger.log(self.level, line)

    def flush(self):
        # Emit any remaining buffered content as a single line
        if self._buffer.strip():
            self.logger.log(self.level, self._buffer.strip())
            self._buffer = ""

def get_stream_writers(logger: Optional[logging.Logger] = None) -> Tuple[LoggerWriter, LoggerWriter]:
    """
    Return (stdout_writer, stderr_writer) that forward to the elecmanage logger.
    If no logger is provided, uses get_logger().
    """
    log = logger or get_logger()
    return LoggerWriter(log, logging.INFO), LoggerWriter(log, logging.ERROR)
