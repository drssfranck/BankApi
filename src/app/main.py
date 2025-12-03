from fastapi import FastAPI
from app.routers import transactions_routes
from app.data.load_data import load_dataset  


app = FastAPI(title="Bank API", version="1.0")

@app.on_event("startup")
def startup_event():
    app.state.df = load_dataset() 
    print("Dataset chargé !")


app.include_router(transactions_routes.router)