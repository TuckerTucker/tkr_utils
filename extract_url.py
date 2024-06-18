import re
from typing import Optional

def extract_url(query: str) -> Optional[str]:
    """
    Extracts the first URL found in the query string.

    Args:
        query (str): The query string to search for a URL.

    Returns:
        Optional[str]: The first URL found in the query, or None if no URL is found.
    """
    url_pattern = re.compile(r'https?://\S+')
    match = url_pattern.search(query)
    return match.group(0) if match else None