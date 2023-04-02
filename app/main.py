from ipaddress import IPv4Address
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from app.httpclient import HTTPXClientWrapper


class Metrics(BaseModel):
    ip_api: dict[str, Any]
    bgview: dict[str, Any]
    total: dict[str, Any]


class RawData(BaseModel):
    ip_api: Optional[dict[str, Any]]
    bgview: Optional[dict[str, Any]]


class IpAnalysisResponse(BaseModel):
    metrics: Metrics
    raw_data: RawData


http_client = HTTPXClientWrapper()
app = FastAPI()


@app.get('/{ip_address}')
@cache(expire=3600)
async def fetch_ip_analysis(ip_address: IPv4Address) -> IpAnalysisResponse:
    pass


@app.on_event('startup')
async def startup():
    FastAPICache.init(InMemoryBackend())
    http_client.start()


@app.on_event('shutdown')
async def shutdown():
    await http_client.stop()

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
