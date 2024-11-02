# tkr_bias_stories/tkr_utils/helper_anthropic/save_responses.py

import json
import os
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from tkr_utils import setup_logging, logs_and_exceptions
from stories.models import StoryResponse
from .models import APIResponse

logger = setup_logging(__file__)

@logs_and_exceptions(logger)
def save_formatted_response(
    output_file: str,
    response: str,
    model: str,
    title: Optional[str] = None,
    hero: Optional[str] = None,
    provider: str = "Anthropic"
) -> None:
    """Save API response in standardized format."""
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
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(formatted_response, file, ensure_ascii=False, indent=2)

        logger.info("Successfully saved response to %s", output_file)
        logger.debug("Response content preview: %s", response[:100] if response else "Empty response")

    except Exception as e:
        logger.error("Failed to save response to %s: %s", output_file, str(e))
        raise

@logs_and_exceptions(logger)
async def save_response_anthropic(
    response: APIResponse,
    story_name: str,
    hero_name: str,
    output_dir: Path
) -> str:
    """Save Anthropic LLM response using standardized format.

    Args:
        response: APIResponse object
        story_name: Name of the story
        hero_name: Name of the hero character
        output_dir: Base directory for saving responses

    Returns:
        str: Path where response was saved
    """
    try:
        # Create provider-specific directory
        story_dir = output_dir / story_name / 'anthropic'
        story_dir.mkdir(parents=True, exist_ok=True)

        logger.debug("Saving response to directory: %s", story_dir)
        logger.debug("Response content type: %s", type(response.content))
        logger.debug("Response content preview: %s", response.content[:100] if response.content else "Empty content")

        # Parse response content
        try:
            content = json.loads(response.content) if isinstance(response.content, str) else response.content
        except json.JSONDecodeError as e:
            logger.error("Failed to parse response content: %s", str(e))
            content = {"text": response.content if response.content else ""}

        # Create standardized response
        standardized_response = StoryResponse(
            story_id=story_name,
            hero=hero_name,
            text=content.get('text', ''),
            metadata={
                'provider': 'anthropic',
                'model': response.metadata.get('model', 'unknown'),
                'total_tokens': response.metadata.get('usage', {}).get('total_tokens', 0),
                'generated_at': datetime.now().isoformat()
            }
        )

        # Create filename from hero name
        hero_filename = f"response_{hero_name.lower().replace(' ', '_')}.json"
        response_path = story_dir / hero_filename

        # Save standardized response
        with open(response_path, 'w', encoding='utf-8') as f:
            json.dump(standardized_response.to_dict(), f, ensure_ascii=False, indent=2)

        logger.info("Successfully saved Anthropic response to %s", response_path)
        return str(response_path)

    except Exception as e:
        logger.error("Error saving Anthropic response: %s", str(e))
        raise
