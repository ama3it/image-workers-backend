import os
from logging.config import dictConfig

LOG_DIR = "logs"
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
               "class": "logging.handlers.RotatingFileHandler",
               "filename": LOG_FILE_PATH,
               "formatter": "default",
               "maxBytes": 10485760,  # 10 MB
               "backupCount": 5,
               "encoding": "utf-8"
            }

        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    }

    dictConfig(logging_config)
