import logging

def req_exception(e: Exception, url: str = "") -> None:
    """
    Handles request exceptions and logs the error.

    Args:
        e (Exception): The exception that occurred.
        url (str): The URL where the request failed.
    """
    logging.error(f"Request failed for {url}: {e}")

def db_exception(e: Exception, query: str = "") -> None:
    """
    Handles database exceptions and logs the error.

    Args:
        e (Exception): The exception that occurred.
        query (str): The SQL query that caused the exception.
    """
    logging.error(f"Database error during query '{query}': {e}")

def stg_exception(e: Exception, filename: str = "") -> None:
    """
    Handles storage exceptions and logs the error.

    Args:
        e (Exception): The exception that occurred.
        filename (str): The name of the file involved in the exception.
    """
    logging.error(f"Storage error for file {filename}: {e}")

def general_exception(e: Exception, context: str = "") -> None:
    """
    Handles general exceptions and logs the error.

    Args:
        e (Exception): The exception that occurred.
        context (str): Additional context about where the error occurred.
    """
    logging.error(f"An unexpected error occurred in {context}: {e}")

__all__ = ["req_exception", "db_exception", "stg_exception", "general_exception"]