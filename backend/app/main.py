from fastapi import FastAPI
from .db.database import engine, Base
from .routers.expenses import router as expenses_router
from .routers.groups import router as groups_router

app = FastAPI(title="Roommate Sync API")
app.include_router(expenses_router)
app.include_router(groups_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Roommate Sync API!"}