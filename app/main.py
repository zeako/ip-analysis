import ipaddress
from typing import Any, Optional

from fastapi import FastAPI
from pydantic import BaseModel


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


app = FastAPI()


@app.get('/{ip_address}')
def fetch_ip_analysis(ip_address: ipaddress.IPv4Address) -> IpAnalysisResponse:
    return IpAnalysisResponse()
