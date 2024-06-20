# mock_module.py
# example of how to use the tkr_utils package

import asyncio
from tkr_utils.app_paths import AppPaths  # Manages application directories and ensures they exist
from tkr_utils.config_logging import setup_logging  # Sets up logging configuration
from tkr_utils.decorators import logs_and_exceptions  # Provides decorators for logging and handling exceptions
from tkr_utils.helper_openai import OpenAIHelper  # Helper class to interact with OpenAI's API

# Setup logging for this module
logger = setup_logging(__file__)

# Ensure necessary directories exist and add a custom directory
# The Storage = True argument is *only* used when adding a new DB
AppPaths.check_directories()
AppPaths.add("custom_data")

@logs_and_exceptions(logger)
def example_function():
    """Example function to demonstrate logging and exception handling."""
    logger.info("Running example_function.")
    return "This is a mock example."

@logs_and_exceptions(logger)
def test_openai_helper_sync():
    """Test function for OpenAIHelper using synchronous mode."""
    logger.info("Testing OpenAIHelper (synchronous).")
    myChat = OpenAIHelper()
    messages = [{"role": "user", "content": "Say this is a test!"}]
    response = myChat.send_message(messages)
    logger.info(f"Response: {response}")
    return response

@logs_and_exceptions(logger)
async def test_openai_helper_async():
    """Test function for OpenAIHelper using asynchronous mode."""
    logger.info("Testing OpenAIHelper (asynchronous).")
    myChat = OpenAIHelper(async_mode=True)
    messages = [{"role": "user", "content": "Say this is a test!"}]
    response = await myChat.send_message_async(messages)
    logger.info(f"Response: {response}")
    return response

if __name__ == "__main__":
    # Run example function
    result = example_function()
    logger.info(result)  # Log the result of example_function

    # Test OpenAIHelper (synchronous)
    openai_response_sync = test_openai_helper_sync()
    logger.info(openai_response_sync)  # Log the response from OpenAI API (sync)

    # Test OpenAIHelper (asynchronous)
    openai_response_async = asyncio.run(test_openai_helper_async())
    logger.info(openai_response_async)  # Log the response from OpenAI API (async)

    # Show usage of AppPaths.DOCS_DIR
    logger.info(f"Documents directory: {AppPaths.DOCS_DIR}")
    logger.info(f"Custom data directory: {AppPaths.CUSTOM_DATA_STORE}")
