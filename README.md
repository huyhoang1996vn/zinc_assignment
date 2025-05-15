# FastAPI Product Rental Service Documentation


This project is a RESTful API service for managing rental products across different regions and rental periods. It enables users to browse products with their attributes, view pricing based on region and rental period, and authenticate for secure access. Built with FastAPI, SQLModel, and MySQL, the service provides high-performance API endpoints with automatic validation, OpenAPI documentation, and database integration.

## Techstack

- Framework: FastAPI
- ORM: SQLModel (combines SQLAlchemy and Pydantic)
- Database: MySQL (with migration support via Alembic)
- Testing: Pytest



## Project Structure

- `main.py` - FastAPI application setup and routes
- `models.py` - Database models using SQLModel
- `endpoints/` - Modular API endpoints
- `alembic/` - Database migrations
- `tests/` - Integration and unit tests



### SQLModel
- Products: Core product information including name, description, and SKU
- Attributes: Product characteristics (e.g., size, color, specifications)
- Regions: Geographic regions where products are available (e.g., Singapore, Malaysia)
- RentalPeriods: Available rental durations (e.g., 3, 6, 12 months)
- ProductPricings: Connects products to regions and rental periods with specific prices


### Database Migrations (Alembic)
Version-controlled schema changes
Upgrades and downgrades between versions
Automatic generation of migration scripts

```bash

# Initialize Alembic (already done)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "init migration"

# Upgrade to latest version
alembic upgrade head

# Downgrade if needed
alembic downgrade -1
```


### Setup and Running
1. Environment Setup:
- Create a .env file with necessary variables following .env.example
- Install dependencies: pip install -r requirements.txt
2. Database Setup:
- Configure database connection in .env
- Run migrations: alembic upgrade head
3. Run the Application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
OR

```bash
fastapi dev main.py
```

4. API Documentation:
Swagger UI: http://localhost:8000/docs


5. API Features
- Pagination: Limit results and navigate through pages
- Filtering: Filter products by region and rental period
- Complete Data: Return products with all related data in a single request


### Testing pytest
The application includes comprehensive tests in tests/test_main.py:

```bash
pytest tests/test_main.py -v
```

### Deployment

- Endpoint: https://assignment-cinch.onrender.com/docs (can slow because free tier)
- Mysql: https://railway.com/



virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt 
docker run -d --name zinc-assignment -p 8000:8000  -e DB_NAME=test_zinc -e SQL_URL=mysql+pymysql://root:steve123@192.168.0.100:3307 zinc

docker build --no-cache -t zinc .

docker exec -it cra_api_app_1 bash


docker run -d \
  --name my-mysql \
  -e MYSQL_ROOT_PASSWORD=steve123 \
  -e MYSQL_USER=steve \
  -e MYSQL_PASSWORD=steve456 \
  -e MYSQL_DATABASE=test_zinc \
  -p 3307:3306 \
  mysql:8 \
  --bind-address=0.0.0.0