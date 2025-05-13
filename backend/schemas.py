from pydantic import BaseModel

class UrlRequest(BaseModel):
    long_url: str
    email: str

class UserLinksRequest(BaseModel):
    email: str

class LinkResponse(BaseModel):
    short_url: str
    long_url: str
    created_at: str

class LinkStatsRequest(BaseModel):
    email: str
    short_url: str
    period: str 