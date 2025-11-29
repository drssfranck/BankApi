from fastapi import FastAPI
from app.routers import transactions_routes

app = FastAPI(title="Card API", version="1.0")
app.include_router(transactions_routes.router)