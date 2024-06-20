# mock_module.py
# example of how to use the tkr_utils package

from tkr_utils.app_paths import AppPaths  # Manages application directories and ensures they exist
from tkr_utils.config_logging import setup_logging  # Sets up logging configuration
from tkr_utils.decorators import logs_and_exceptions  # Provides decorators for logging and handling exceptions
from tkr_utils.helper_openai import OpenAIHelper  # Helper class to interact with OpenAI's API

# Setup logging for this module
logger = setup_logging(__file__)

# Ensure necessary directories exist and add a custom directory
AppPaths.check_directories()
AppPaths.add("custom_data", storage=True)

@logs_and_exceptions(logger)
def example_function():
    """Example function to demonstrate logging and exception handling."""
    logger.info("Running example_function.")
    return "This is a mock example."

@logs_and_exceptions(logger)
def test_openai_helper():
    """Test function for OpenAIHelper."""
    logger.info("Testing OpenAIHelper.")
    myChat = OpenAIHelper()
    messages = [{"role": "user", "content": "Say this is a test!"}]
    response = myChat.send_message(messages)
    logger.info(f"Response: {response}")
    return response

if __name__ == "__main__":
    # Run example function
    result = example_function()
    logger.info(result)  # Log the result of example_function

    # Test OpenAIHelper
    openai_response = test_openai_helper()
    logger.info(openai_response)  # Log the response from OpenAI API

    # Show usage of AppPaths.DOCS_DIR
    logger.info(f"Documents directory: {AppPaths.DOCS_DIR}")
    logger.info(f"Custom data directory: {AppPaths.CUSTOM_DATA_STORE}")
