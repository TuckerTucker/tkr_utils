# tkr_bias_stories/tkr_utils/helper_anthropic/save_responses.py
import json
from typing import Optional
from tkr_utils import setup_logging

logger = setup_logging(__file__)

def save_formatted_response(
    output_file: str,
    response: str,
    model: str,
    title: Optional[str] = None,
    hero: Optional[str] = None,
    provider: str = "Anthropic"
) -> None:
    """Save API response in standardized format.

    Args:
        output_file: Path to output file
        response: Response text from API
        model: Model name used for generation
        title: Optional story title
        hero: Optional story hero
        provider: API provider name, defaults to Anthropic
    """
    formatted_response = {
        "story": {
            "title": title or "Untitled",
            "hero": hero or "Unknown",
            "llm": {
                "provider": provider,
                "model": model
            },
            "response": {
                "text": response
            }
        }
    }

    try:
        with open(output_file, 'a') as file:
            json_str = json.dumps(formatted_response, ensure_ascii=True, indent=2)
            file.write(json_str + "\n")
        logger.debug("Response saved successfully to %s", output_file)
    except IOError as e:
        logger.error("Failed to save response to %s: %s", output_file, str(e))
        raise
