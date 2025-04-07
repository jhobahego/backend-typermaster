from fastapi import APIRouter
from services import text_generator

router = APIRouter()

@router.get("/texts", tags=["Texts"])
async def get_random_text_endpoint():
    """
    Endpoint to get a random text for the typing test.
    """
    generated_text = await text_generator.generate_typing_text()
    return {"text": generated_text}
