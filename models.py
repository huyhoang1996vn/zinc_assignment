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
    



data_columns = ['Sale Date', 'Client ID', 'Sale ID', 'Item name', 'Batch #', 'Sales Notes', 'Location', 'Notes', 'Color', 'Size', 'Item price (excluding tax)', 'Quantity', 'Subtotal (excluding tax)', 'Discount %', 'Discount amount', 'Tax', 'Item Total', 'Total Paid w/ Payment Method', 'Payment Method']

db_columns = ['sale_date', 'client_id', 'sale_id', 'item_name', 'batch', 'sales_notes', 'location', 'notes', 'color', 'size', 'item_price_excluding_tax', 'quantity', 'subtotal_excluding_tax', 'discount', 'discount_amount', 'tax', 'item_total', 'total_paid_payment_method', 'payment_method']

data_columns = ['Sale Date', 'Sale ID', 'Total Paid w/ Payment Method', 'Item name']
db_columns = ['date', 'order_id', 'amount_sgd', 'product_id']