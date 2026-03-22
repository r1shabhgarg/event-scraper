from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.database import get_db
from db import crud
import schemas

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=List[schemas.EventResponse])
async def read_events(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="Filter by event type"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort: Optional[str] = Query(None, description="Sort by 'date' for upcoming"),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_events(
        db=db, skip=skip, limit=limit, 
        event_type=type, tag=tag, sort_by_date=(sort == "date")
    )

@router.get("/recommended", response_model=List[schemas.EventResponse])
async def get_recommended(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await crud.get_events(db=db, skip=skip, limit=limit, recommended=True)

@router.get("/ending-soon", response_model=List[schemas.EventResponse])
async def get_ending_soon(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await crud.get_events(db=db, skip=skip, limit=limit, ending_soon=True)

from services.ai_search import aggregate_search

@router.post("/search", response_model=schemas.SearchResponse)
async def ai_search_endpoint(
    request: schemas.SearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced AI Search Agent Endpoint mapping DDG, Serper, and Internal APIs via an LLM.
    """
    return await aggregate_search(db=db, query=request.query)

