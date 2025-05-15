import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from alembic import command
from alembic.config import Config
from endpoints.api import api_router


class LogRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        endpoint = request.url.path
        params = dict(request.query_params)

        logger.bind(
            endpoint=endpoint,
            request_id=request_id,
            parameters=params
        ).info(f"Request received {request_id} {endpoint} {params}")

        response = await call_next(request)

        logger.bind(
            endpoint=endpoint,
            request_id=request_id,
            parameters=params
        ).info(f"Response sent with status {response.status_code}")

        return response


def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.error("Starting run_migrations: ")
        logger.error(f"Starting run_migrations: {e}")
        


@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info("Starting up...")
    run_migrations()
    logger.info("Done run alembic upgrade head...")
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(LogRequestMiddleware)

app.include_router(api_router)

