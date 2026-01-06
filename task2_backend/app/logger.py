import logging
import sys

def setup_logger():
    logger = logging.getLogger("fynd_ai_backend")
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
