from fastapi import APIRouter, HTTPException
from schemas.scrape import ScrapeRequest
from schemas.vehicle import Vehicle
from services.scraper import ScraperService
from utils.executor import run_in_thread

router = APIRouter(
    prefix="/scrape",
    tags=["Scraping"],
)

@router.post("/", response_model=Vehicle)
async def scrape_website(payload: ScrapeRequest):
    try:
        result = await run_in_thread(
            ScraperService.scrape,
            str(payload.url),
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )