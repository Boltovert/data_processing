import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from src.app_container import ApplicationContainer
from src.router import api_router
from src.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("[LIFESPAN] Starting...")
    container = ApplicationContainer()
    os.environ["JOB_NAME"] = "app_server"
    print("[LIFESPAN] Before init_resources")
    await container.init_resources()
    print("[LIFESPAN] After init_resources")
    yield
    print("[LIFESPAN] Shutting down resources...")
    await container.shutdown_resources()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs/",
    openapi_url="/api/openapi.json1",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)


def run_app():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=1337,
        log_level=settings.log_level,
        reload=settings.server.reload,
    )


if __name__ == "__main__":
    run_app()
