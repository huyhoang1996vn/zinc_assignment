# Add these imports at the top of main.py
from pydantic import BaseModel
from datetime import date


class MetricDailysResponse(BaseModel):
    date: date
    revenue_sgd: float
