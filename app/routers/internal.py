import time
from fastapi import APIRouter, HTTPException
from services.scraper import ScraperService
from utils.executor import run_in_thread

router = APIRouter(prefix="/internal", tags=["Internal RPC"])


@router.post("/scrape")
async def internal_scrape(payload: dict):
    if payload.get("method") != "scrape":
        raise HTTPException(status_code=400, detail="Invalid method")

    params = payload.get("params", {})
    url = params.get("url")

    if not url:
        raise HTTPException(status_code=400, detail="URL required")

    start = time.time()

    result = await run_in_thread(
        ScraperService.scrape,
        url,
        params,
    )

    duration = int((time.time() - start) * 1000)

    return {
        "success": True,
        "data": result,
        "meta": {
            "duration_ms": duration,
            "source": "html",
        },
    }
