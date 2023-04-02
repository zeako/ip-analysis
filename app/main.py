from ipaddress import IPv4Address
import time
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from app.httpclient.httpclient import HTTPXClientWrapper


class Metric(BaseModel):
    status: str # can use enum
    time: int


class Metrics(BaseModel):
    ip_api: Metric
    bgview: Metric
    total: Metric


class RawData(BaseModel):
    ip_api: Optional[dict[str, Any]]
    bgpview: Optional[dict[str, Any]]


class IpAnalysisResponse(BaseModel):
    metrics: Metrics
    raw_data: RawData


http_client = HTTPXClientWrapper()
app = FastAPI()


@app.get('/{ip_address}')
@cache(expire=3600)
async def fetch_ip_analysis(ip_address: IPv4Address) -> IpAnalysisResponse:
    async_client = http_client()

    start_time = time.monotonic()

    ip_api_start = start_time
    ip_api_res = await async_client.get(f'http://ip-api.com/json/{ip_address}')
    ip_api_res_end = time.monotonic() - ip_api_start


    bgpview_start = time.monotonic()
    bgpview_res = await async_client.get(f'https://api.bgpview.io/ip/{ip_address}')
    bgpview_res_end = time.monotonic() - bgpview_start

    total_time = time.monotonic() - start_time

    metrics = Metrics(
        ip_api=Metric(
            status='success' if ip_api_res.is_success else 'failure',
            time=ip_api_res_end
        ),
        bgview=Metric(
            status='success' if bgpview_res.is_success else 'failure',
            time=bgpview_res_end
        ),
        total=Metric(
            status='success' if ip_api_res.is_success and bgpview_res.is_success else 'failure',
            time=total_time
        )
    )

    return IpAnalysisResponse(
        metrics=metrics,
        raw_data=RawData(
            ip_api=ip_api_res.json(),
            bgpview=bgpview_res.json()
        ))


@app.on_event('startup')
async def startup():
    FastAPICache.init(InMemoryBackend())
    http_client.start()


@app.on_event('shutdown')
async def shutdown():
    await http_client.stop()

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
