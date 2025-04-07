from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models.game_result import GameResult

from schemas.game_result import GameResultCreate, GameResultResponse, PaginatedGameResults

from config.database import get_db

router = APIRouter()

@router.post("/results", response_model=GameResultResponse, tags=["Results"])
async def save_result_endpoint(
    result: GameResultCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint to save a game result to the database.
    """
    db_result = GameResult(**result.model_dump()) # Use model_dump for Pydantic v2
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@router.get("/results", response_model=PaginatedGameResults, tags=["Results"])
async def get_results_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve paginated game results, ordered by creation date descending.
    """
    # Calculate offset
    offset = (page - 1) * per_page

    # Query for total count
    total = db.query(func.count(GameResult.id)).scalar()

    # Query for paginated results
    query_results = db.query(GameResult)\
        .order_by(desc(GameResult.created_at))\
        .offset(offset)\
        .limit(per_page)\
        .all()

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert results using the Pydantic schema for proper serialization
    results_response = [GameResultResponse.model_validate(res) for res in query_results]

    return PaginatedGameResults(
        results=results_response,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages
    )
