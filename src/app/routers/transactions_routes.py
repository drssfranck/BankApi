from fastapi import APIRouter, Request, HTTPException
import json
router = APIRouter()


@router.get("/transactions")
def get_transactions(request: Request):
    df = request.app.state.df
    return json.loads(df.head().to_json(orient="records"))

