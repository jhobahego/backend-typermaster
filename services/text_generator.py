import logging

from google import genai

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API using the key from settings
try:
    client = genai.Client(api_key=settings.gemini_api_key)
    logger.info("Gemini API configured successfully.")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    client = None  # Ensure client is None if configuration fails


prompt_large_text = "Generate a medium-length text in English suitable for a typing test. The text should be no more than one paragraph of between 5 and 8 lines of 8 to 14 words, taking into account the length of the words. If many short connectors are used, then use the maximum number of words; however, if long words are used, there should be fewer words per line. Make sure the text is coherent and tells a story. IMPORTANT: Respond ONLY with the generated text, without any introduction, explanation, or formatting such as quotes."

prompt_medium_text = "Generate a medium-length text in English suitable for a typing test. The text should be no more than one paragraph of between 3 and 5 lines of 8 to 14 words, taking into account the length of the words. If many short connectors are used, then use the maximum number of words; however, if long words are used, there should be fewer words per line. Make sure the text is coherent and tells a story. IMPORTANT: Respond ONLY with the generated text, without any introduction, explanation, or formatting such as quotes."

prompt_short_text = "Generate a medium-length text in English suitable for a typing test. The text should be no more than one paragraph of between 1 and 3 lines of 8 to 14 words, taking into account the length of the words. If many short connectors are used, then use the maximum number of words; however, if long words are used, there should be fewer words per line. Make sure the text is coherent and tells a story. IMPORTANT: Respond ONLY with the generated text, without any introduction, explanation, or formatting such as quotes."


async def generate_typing_text() -> str:
    """
    Generates a short English text suitable for a typing test using the Gemini API.
    Provides a fallback text if the API call fails.
    """
    if not client:
        logger.error("Gemini client not initialized. Returning fallback text.")
        return "The quick brown fox jumps over the lazy dog."  # Fallback

    try:
        prompt = prompt_short_text
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=prompt
        )

        logger.info(f"Gemini API responded with: {response.text}")

        # Basic error handling/check if response has text
        if response.text:
            # Clean up potential markdown or extra whitespace
            generated_text = response.text.strip()
            # Remove potential quotes if the model wraps the text (less likely with updated prompt)
            if generated_text.startswith('"') and generated_text.endswith('"'):
                generated_text = generated_text[1:-1].strip()
            if generated_text.startswith("'") and generated_text.endswith("'"):
                generated_text = generated_text[1:-1].strip()

            logger.info("Successfully generated text using Gemini.")
            return generated_text
        else:
            logger.warning("Gemini response did not contain text. Returning fallback.")
            # Fallback or raise error if generation fails
            return "The quick brown fox jumps over the lazy dog."  # Fallback
    except Exception as e:
        logger.error(f"Error generating text with Gemini: {e}")
        # Fallback in case of API error
        return "Error generating text. Please try again later."  # Fallback indicating error
