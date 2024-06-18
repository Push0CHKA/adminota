from loguru import logger

from src.api.app.app import API


def main():
    api = API()
    try:
        api.run()
    except KeyboardInterrupt:
        logger.warning("Force stop application")
    except Exception as e:
        logger.critical(
            f"Application was stopped with unhandled error. Reason: {e}"
        )
