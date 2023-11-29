import logging

DEFAULT_LOG_FORMAT = '[%(asctime)s] {%(filename)s} %(levelname)s: %(message)s'
LOGGERS_TO_SILENCE = {
    'requests': logging.WARNING,
    'urllib3': logging.ERROR,
    'selenium': logging.WARNING,
}

def set_logger_config(
    log_level = logging.INFO, 
    log_format = DEFAULT_LOG_FORMAT, 
    date_format = None,
    loggers_to_adjust = LOGGERS_TO_SILENCE
):
    """
    Sets the log format for all loggers using `logging.basicConfig`,
    and also changes the level on the `loggers_to_adjust`

    Parameters
    ----------
    log_level: int, optional
        Level of the main root logger
    log_format: str
        Logs string format
    date_format: str
        Logs date format
    loggers_to_adjust: dict[str], optional
        Loggers whose verbosity is adjusted
    """
    logging.basicConfig(
        format = log_format, 
        datefmt = date_format, 
        level = log_level
    )

    # change verbosity on some loggers
    for logger_name, log_level in loggers_to_adjust.items():
        logging.getLogger(logger_name).setLevel(log_level)
