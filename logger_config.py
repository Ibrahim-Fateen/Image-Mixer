import logging
from datetime import datetime
import os


def setup_logger(name, log_dir='logs/', level=logging.DEBUG):
    """Setup a logger for a specific module or class."""
    # create log_dir if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = f"{log_dir}ImageMixer_{current_time}.log"

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    # Set handler levels
    file_handler.setLevel(level)
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    if not logger.hasHandlers():  # Prevent adding handlers multiple times
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
