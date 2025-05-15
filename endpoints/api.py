from fastapi import APIRouter
from .sales import sale_router

api_router = APIRouter()
api_router.include_router(sale_router)