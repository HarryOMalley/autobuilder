from loguru import logger

logger.add(
    "file.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
