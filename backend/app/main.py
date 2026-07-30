from fastapi import FastAPI

from app.api.routes.user import router as user_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.transaction import router as transaction_router
from app.api.routes.holding import router as holding_router
from app.api.routes.summary import router as summary_router
app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "QuantForge API is running!"
    }


app.include_router(user_router)
app.include_router(portfolio_router)
app.include_router(transaction_router)
app.include_router(holding_router)
app.include_router(summary_router)