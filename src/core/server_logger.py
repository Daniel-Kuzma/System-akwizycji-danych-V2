import logging
import sys

logger = logging.getLogger()

formatter = logging.Formatter(
    fmt = "%(asctime)s | %(levelname)s | %(funcName)s | %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout) # wysyłanie do konsoli (potem do usunięcia)
file_handler = logging.FileHandler("logs.log")

stream_handler.setFormatter(formatter) # wysyłanie do konsoli (potem do usunięcia)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler) # wysyłanie do konsoli (potem do usunięcia)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)
