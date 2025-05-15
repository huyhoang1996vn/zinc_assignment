from sqlmodel import Field, SQLModel
from datetime import datetime, date
from typing import Optional

metadata = SQLModel.metadata


class Sale(SQLModel, table=True):
    id: int = Field(primary_key=True)
    date: date
    order_id: str
    amount_sgd: float
    product_id: str
    
