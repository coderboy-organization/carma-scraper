from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers.scrape import router as scrape_router
from routers.internal import router as internal_router

app = FastAPI(
    title="Carmasearch Scraper API",
    version="1.0.0",
    description="Carmasearch Scraper API"
)

@app.get("/")
async def root():
    res:dict = {
        "status": "Running..."
    }
    return JSONResponse(content=res, status_code=200)

app.include_router(internal_router)
app.include_router(scrape_router)