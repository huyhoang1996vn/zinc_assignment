import io

import pandas as pd
from fastapi import APIRouter, Query, UploadFile, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.sql import text
from sqlmodel import func, select
from endpoints.base_models import *
from models import *
from settings import SessionDep

sale_router = APIRouter(tags=["Sale"], prefix="/api")


@sale_router.post("/import-sales/")
async def import_sales(
    file: UploadFile,
    session: SessionDep,
):
    try:
        data_columns = [
            "Sale Date",
            "Sale ID",
            "Item name",
            "Total Paid w/ Payment Method",
        ]
        db_columns = ["date_str", "order_id", "product_id", "amount_sgd"]
        contents = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(
                io.StringIO(contents.decode("utf-8")), usecols=data_columns
            )
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(contents), usecols=data_columns)
        else:
            return JSONResponse(
                content={"error": "Unsupported file format"}, status_code=400
            )

        df.columns = db_columns
        df["date"] = df["date_str"].apply(
            lambda x: datetime.strptime(x, "%m/%d/%Y").date()
        )
        df.drop("date_str", axis=1, inplace=True)

        sale_data = df.to_dict(orient="records")
        session.bulk_insert_mappings(Sale, sale_data)
        session.commit()
        result = session.exec(select(func.count()).select_from(Sale)).one()
        return JSONResponse(
            content={"imported_rows": result}, status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Exception in import_sales: {e}")
        return JSONResponse(
            content={"detail": {e}}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@sale_router.get("/metrics/revenue/")
async def metrics_revenue(
    session: SessionDep,
    start_date: date = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: date = Query(
        description="End date in YYYY-MM-DD format",
    ),
):
    try:
        if end_date < start_date:
            return JSONResponse(
                content={"detail": "End date must greater than start date"},
                status_code=400,
            )

        results = session.execute(
            text(
                """
               SELECT 
                ROUND(SUM(amount_sgd), 2) AS total_revenue_sgd,
                ROUND(AVG(amount_sgd), 2) AS average_order_value_sgd
            FROM sale
            WHERE sale.date BETWEEN :start_date AND :end_date
            """
            ),
            {"start_date": start_date, "end_date": end_date},
        ).all()
        result_dict = [dict(row._mapping) for row in results]
        return JSONResponse(content=result_dict, status_code=200)
    except Exception as e:
        logger.error(f"Exception in metrics_revenue: {e}")
        return JSONResponse(
            content={"detail": {e}}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@sale_router.get("/metrics/revenue/daily", response_model=list[MetricDailysResponse])
async def metrics_revenue_daily(
    session: SessionDep,
    start_date: date = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: date = Query(
        description="End date in YYYY-MM-DD format",
    ),
):
    try:
        if end_date < start_date:
            return JSONResponse(
                content={"detail": "End date must greater than start date"},
                status_code=400,
            )

        results = session.execute(
            text(
                """
                SELECT 
                    sale.date as date,
                    ROUND(SUM(amount_sgd), 2) AS revenue_sgd
                FROM sale
                WHERE sale.date BETWEEN :start_date AND :end_date
                GROUP BY date
            """
            ),
            {"start_date": start_date, "end_date": end_date},
        ).all()

        result_dict = [dict(row._mapping) for row in results]
        return result_dict
    except Exception as e:
        logger.error(f"Exception in metrics_revenue_daily: {e}")
        return JSONResponse(
            content={"detail": {e}}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@sale_router.get("/health/")
async def health_check(session: SessionDep):
    try:
        session.execute(text("SELECT 1"))
        return JSONResponse(
            content={"status": "ok", "database": "reachable"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "database": "unreachable", "error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
