import logging


logging.basicConfig(
    level=logging.INFO,
    style="{",
    format="{asctime} | {levelname} | {message}",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)