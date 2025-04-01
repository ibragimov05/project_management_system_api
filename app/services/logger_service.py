from logging import INFO, Logger, getLogger

import colorlog

# Set up colorlog handler
log_format = "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
color_handler = colorlog.StreamHandler()
color_handler.setFormatter(colorlog.ColoredFormatter(log_format))

# Set up the logger
logger: Logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(color_handler)
