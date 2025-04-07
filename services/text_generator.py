import google.generativeai as genai
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API using the key from settings
try:
    genai.configure(api_key=settings.gemini_api_key)
    # Select the model (consider making this configurable)
    model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
    logger.info("Gemini API configured successfully.")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    model = None # Ensure model is None if configuration fails

async def generate_typing_text() -> str:
    """
    Generates a short English text suitable for a typing test using the Gemini API.
    Provides a fallback text if the API call fails.
    """
    if not model:
        logger.error("Gemini model not initialized. Returning fallback text.")
        return "The quick brown fox jumps over the lazy dog." # Fallback

    try:
        # Updated prompt to explicitly ask for only the text
        prompt = "Generate a short English text suitable for a typing test. It should be a single paragraph, between 1 and 4 lines long. IMPORTANT: Respond ONLY with the generated text itself, without any introduction, explanation, or formatting like quotes."
        response = await model.generate_content_async(prompt) # Use async version

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
            return "The quick brown fox jumps over the lazy dog." # Fallback
    except Exception as e:
        logger.error(f"Error generating text with Gemini: {e}")
        # Fallback in case of API error
        return "Error generating text. Please try again later." # Fallback indicating error
