from fastapi import FastAPI

from app.api.routes.user import router as user_router
from app.api.routes.portfolio import router as portfolio_router
app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "QuantForge API is running!"
    }


app.include_router(user_router)
app.include_router(portfolio_router)