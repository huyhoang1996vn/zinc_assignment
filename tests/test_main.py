import io
import time
from datetime import datetime

import pandas as pd
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, create_engine, func, select

from endpoints.sales import sale_router
# from app.database import Base  # Replace app with your app's name
from main import app
from models import Sale
from settings import SessionDep, get_session

# Seconds since epoch
unix_timestamp = str(int(time.time())) 
file_path = f"./test_{unix_timestamp}.db"
test_engine = create_engine(f"sqlite:///{file_path}", echo=True)

@pytest.fixture(scope="function")
def test_session():
    """Create a fresh database for each test."""
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    # Create a new session
    session = Session(test_engine)
    
    # Override the session dependency
    def override_get_session():
        try:
            yield session
        finally:
            session.close()
    
    # # Override the dependency
    # app.dependency_overrides[SessionDep] = override_get_session
    
    yield session
    
    # Clean up after test
    session.close()

@pytest.fixture()
def client(test_session):
    def override_get_db():
        try:
            yield test_session
        finally:
            test_session.close()

    app.dependency_overrides[get_session] = override_get_db
    client = TestClient(app)
    yield client

def test_read_main(client):
    response = client.get("/docs")
    assert response.status_code == 200

def test_import_sales(client, test_session):
    """Test importing sales data and verify database row count and imported_rows log."""
    # Create test data
    test_data = {
        "Sale Date": ["05/12/2024", "05/13/2024"],
        "Sale ID": ["ORDER001", "ORDER002"],
        "Item name": ["Product1", "Product2"],
        "Total Paid w/ Payment Method": [100.50, 200.75]
    }
    df = pd.DataFrame(test_data)
    
    # Create a CSV file in memory
    csv_file = io.BytesIO()
    df.to_csv(csv_file, index=False)
    csv_file.seek(0)
    
    # Get initial row count
    initial_count = test_session.exec(select(func.count()).select_from(Sale)).one()
    
    # Make the API request
    files = {"file": ("test_sales.csv", csv_file, "text/csv")}
    response = client.post("/api/import-sales/", files=files)
    
    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "imported_rows" in data
    
    # Verify database row count
    final_count = test_session.exec(select(func.count()).select_from(Sale)).one()
    expected_new_rows = len(test_data["Sale Date"])
    assert final_count == initial_count + expected_new_rows
    
    # Verify imported_rows matches the new row count
    assert data["imported_rows"] == final_count
    
    # Verify the data was imported correctly
    imported_sales = test_session.exec(select(Sale).order_by(Sale.id.desc()).limit(2)).all()
    assert len(imported_sales) == 2
    
    # Verify first imported sale
    assert imported_sales[0].order_id == "ORDER002"
    assert imported_sales[0].product_id == "Product2"
    assert imported_sales[0].amount_sgd == 200.75
    assert imported_sales[0].date == datetime.strptime("05/13/2024", "%m/%d/%Y").date()
    
    # Verify second imported sale
    assert imported_sales[1].order_id == "ORDER001"
    assert imported_sales[1].product_id == "Product1"
    assert imported_sales[1].amount_sgd == 100.50
    assert imported_sales[1].date == datetime.strptime("05/12/2024", "%m/%d/%Y").date()
    
from datetime import date, timedelta


def test_metrics_revenue(client, test_session):
    """Test revenue metrics endpoint with 5 seeded sales."""
    # Create 5 test sales
    base_date = date(2024, 5, 1)
    sales_data = [
        Sale(
            date=base_date + timedelta(days=i),
            order_id=f"ORDER{i+1:03d}",
            product_id=f"Product{i+1}",
            amount_sgd=100.00 * (i + 1)  # 100, 200, 300, 400, 500
        )
        for i in range(5)
    ]
    
    # Add sales to database
    for sale in sales_data:
        test_session.add(sale)
    test_session.commit()
    
    # Calculate expected values
    total_revenue = sum(sale.amount_sgd for sale in sales_data)  # 1500.00
    average_order_value = total_revenue / len(sales_data)  # 300.00
    
    # Make the API request
    response = client.get(
        f"/api/metrics/revenue/?start_date={base_date}&end_date={base_date + timedelta(days=4)}"
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1  # Should return one row with totals
    
    # Verify metrics
    metrics = data[0]
    assert metrics["total_revenue_sgd"] == 1500.00
    assert metrics["average_order_value_sgd"] == 300.00    
    
    
def test_metrics_revenue_daily(client, test_session):
    """Test daily revenue metrics endpoint with sales spanning three dates."""
    # Create test sales spanning three dates
    base_date = date(2024, 4, 1)
    sales_data = [
        # Day 1: Two sales
        Sale(
            date=base_date,
            order_id="ORDER001",
            product_id="Product1",
            amount_sgd=100.00
        ),
        Sale(
            date=base_date,
            order_id="ORDER002",
            product_id="Product2",
            amount_sgd=200.00
        ),
        # Day 2: One sale
        Sale(
            date=base_date + timedelta(days=1),
            order_id="ORDER003",
            product_id="Product3",
            amount_sgd=300.00
        ),
        # Day 3: Two sales
        Sale(
            date=base_date + timedelta(days=2),
            order_id="ORDER004",
            product_id="Product4",
            amount_sgd=400.00
        ),
        Sale(
            date=base_date + timedelta(days=2),
            order_id="ORDER005",
            product_id="Product5",
            amount_sgd=500.00
        ),
    ]
    
    # Add sales to database
    for sale in sales_data:
        test_session.add(sale)
    test_session.commit()
    
    # Make the API request
    response = client.get(
        f"/api/metrics/revenue/daily/?start_date={base_date}&end_date={base_date + timedelta(days=2)}"
    )
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3  # Should return three days of data
    
    # Verify each day's revenue
    # Day 1: 100 + 200 = 300
    assert data[0]["date"] == base_date.isoformat()
    assert data[0]["revenue_sgd"] == 300.00
    
    # Day 2: 300
    assert data[1]["date"] == (base_date + timedelta(days=1)).isoformat()
    assert data[1]["revenue_sgd"] == 300.00
    
    # Day 3: 400 + 500 = 900
    assert data[2]["date"] == (base_date + timedelta(days=2)).isoformat()
    assert data[2]["revenue_sgd"] == 900.00    
    
    
def test_health_check(client):
    """Test health check endpoint returns ok status."""
    response = client.get("/api/health/")
    
    # Verify response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "reachable"    
    
