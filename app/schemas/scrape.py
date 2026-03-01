from pydantic import BaseModel, HttpUrl


class ScrapeRequest(BaseModel):
    url: HttpUrl


class ScrapeResponse(BaseModel):
    url: HttpUrl
    title: str
