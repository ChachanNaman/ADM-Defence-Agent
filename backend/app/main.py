from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import adm, agent, decision

app = FastAPI(title="ADM Defense Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(adm.router)
app.include_router(agent.router)
app.include_router(decision.router)


@app.get("/health")
def health():
    return {"status": "ok"}
