import logging
import logging.config

def configure_logging(log_level):
    # Configure logging
    LOG_LEVEL_DEFAULT = "INFO"
    
    if log_level not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]:
        logging.warning(
            f"LOG_LEVEL sholud be set to one of these values: [CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET]. Falling back to INFO"
        )
        log_level = LOG_LEVEL_DEFAULT

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | [%(name)s:%(lineno)d] [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(asctime)s:%(name)s %(message)s",
            },
        },
        "handlers": {
            "h": {
                "formatter": "default",
                "level": log_level,
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {__name__: {"level": log_level, "handlers": "h"}},
        "root": {
            "level": log_level,
            "handlers": [
                "h",
            ],
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)

    # logger = logging.getLogger(__name__)
    logger = logging.getLogger()
