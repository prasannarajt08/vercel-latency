from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from typing import List

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "86400",
}


@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    response = await call_next(request)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


DATA = [{"region": "apac", "service": "catalog", "latency_ms": 158.84, "uptime_pct": 97.43, "timestamp": 20250301}, {"region": "apac", "service": "recommendations", "latency_ms": 211.96, "uptime_pct": 98.402, "timestamp": 20250302}, {"region": "apac", "service": "support", "latency_ms": 165.73, "uptime_pct": 98.466, "timestamp": 20250303}, {"region": "apac", "service": "support", "latency_ms": 128.94, "uptime_pct": 98.115, "timestamp": 20250304}, {"region": "apac", "service": "catalog", "latency_ms": 159.18, "uptime_pct": 98.726, "timestamp": 20250305}, {"region": "apac", "service": "analytics", "latency_ms": 175.56, "uptime_pct": 98.317, "timestamp": 20250306}, {"region": "apac", "service": "analytics", "latency_ms": 185.85, "uptime_pct": 98.25, "timestamp": 20250307}, {"region": "apac", "service": "checkout", "latency_ms": 178.83, "uptime_pct": 98.38, "timestamp": 20250308}, {"region": "apac", "service": "payments", "latency_ms": 171.04, "uptime_pct": 97.867, "timestamp": 20250309}, {"region": "apac", "service": "payments", "latency_ms": 136.05, "uptime_pct": 99.416, "timestamp": 20250310}, {"region": "apac", "service": "recommendations", "latency_ms": 217.54, "uptime_pct": 99.149, "timestamp": 20250311}, {"region": "apac", "service": "catalog", "latency_ms": 189.88, "uptime_pct": 99.193, "timestamp": 20250312}, {"region": "emea", "service": "payments", "latency_ms": 195.73, "uptime_pct": 98.901, "timestamp": 20250301}, {"region": "emea", "service": "recommendations", "latency_ms": 133.49, "uptime_pct": 97.453, "timestamp": 20250302}, {"region": "emea", "service": "recommendations", "latency_ms": 171.84, "uptime_pct": 97.948, "timestamp": 20250303}, {"region": "emea", "service": "recommendations", "latency_ms": 185.32, "uptime_pct": 99.121, "timestamp": 20250304}, {"region": "emea", "service": "catalog", "latency_ms": 134.05, "uptime_pct": 97.166, "timestamp": 20250305}, {"region": "emea", "service": "payments", "latency_ms": 220.51, "uptime_pct": 98.423, "timestamp": 20250306}, {"region": "emea", "service": "checkout", "latency_ms": 109.9, "uptime_pct": 98.54, "timestamp": 20250307}, {"region": "emea", "service": "recommendations", "latency_ms": 202.82, "uptime_pct": 97.922, "timestamp": 20250308}, {"region": "emea", "service": "checkout", "latency_ms": 116.25, "uptime_pct": 99.419, "timestamp": 20250309}, {"region": "emea", "service": "recommendations", "latency_ms": 218.15, "uptime_pct": 97.211, "timestamp": 20250310}, {"region": "emea", "service": "recommendations", "latency_ms": 187.69, "uptime_pct": 99.383, "timestamp": 20250311}, {"region": "emea", "service": "payments", "latency_ms": 159.05, "uptime_pct": 97.3, "timestamp": 20250312}, {"region": "amer", "service": "payments", "latency_ms": 123.86, "uptime_pct": 99.012, "timestamp": 20250301}, {"region": "amer", "service": "payments", "latency_ms": 235.68, "uptime_pct": 98.338, "timestamp": 20250302}, {"region": "amer", "service": "payments", "latency_ms": 153.66, "uptime_pct": 99.175, "timestamp": 20250303}, {"region": "amer", "service": "analytics", "latency_ms": 239.76, "uptime_pct": 97.958, "timestamp": 20250304}, {"region": "amer", "service": "recommendations", "latency_ms": 118.94, "uptime_pct": 97.956, "timestamp": 20250305}, {"region": "amer", "service": "recommendations", "latency_ms": 108.18, "uptime_pct": 98.774, "timestamp": 20250306}, {"region": "amer", "service": "catalog", "latency_ms": 208.62, "uptime_pct": 98.62, "timestamp": 20250307}, {"region": "amer", "service": "checkout", "latency_ms": 180.4, "uptime_pct": 97.751, "timestamp": 20250308}, {"region": "amer", "service": "checkout", "latency_ms": 149.7, "uptime_pct": 97.139, "timestamp": 20250309}, {"region": "amer", "service": "support", "latency_ms": 169.24, "uptime_pct": 97.722, "timestamp": 20250310}, {"region": "amer", "service": "support", "latency_ms": 174.86, "uptime_pct": 99.37, "timestamp": 20250311}, {"region": "amer", "service": "catalog", "latency_ms": 133.11, "uptime_pct": 98.722, "timestamp": 20250312}]


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float


def percentile(values, p):
    # linear interpolation (same as numpy.percentile default)
    s = sorted(values)
    k = (len(s) - 1) * p / 100
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


@app.post("/")
@app.post("/api")
@app.post("/api/index")
def analyze(q: Query):
    out = {}
    for region in q.regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime_pct"] for r in rows]
        out[region] = {
            "avg_latency": sum(lat) / len(lat),
            "p95_latency": percentile(lat, 95),
            "avg_uptime": sum(up) / len(up),
            "breaches": sum(1 for x in lat if x > q.threshold_ms),
        }
    return {"regions": out}
