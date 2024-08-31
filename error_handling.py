import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the default logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler(),  # Log to the console
    ],
)

logger = logging.getLogger(__name__)


def some_function():
    try:
        # Simulate an operation that could raise an exception
        result = 10 / 0
    except Exception as e:
        logger.error(
            "An error occurred in some_function", exc_info=True
        )  # Log the error with traceback


def another_function():
    try:
        # Simulate another potential failure
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
    except Exception as e:
        logger.error("An error occurred in another_function", exc_info=True)


if __name__ == "__main__":
    logger.info("Starting the application...")
    some_function()
    another_function()
    logger.info("Application finished.")
