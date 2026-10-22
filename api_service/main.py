from fastapi import FastAPI

from api_service.routers import all_routers

app = FastAPI(title="TSP CRM", version="1.0.0")

for r in all_routers:
    app.include_router(r)


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}