from fastapi import FastAPI
from .db.database import engine, Base
from .routers.expenses import router as expenses_router
from .routers.groups import router as groups_router
from .routers.settlements import router as settlements_router
from fastapi.middleware.cors import CORSMiddleware
from .routers.users import router as users_router

app = FastAPI(title="Roommate Sync API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # 允許 Vite 前端的網址
    allow_credentials=True,
    allow_methods=["*"], # 允許所有方法 (GET, POST 等)
    allow_headers=["*"], # 允許所有 Headers
)

app.include_router(expenses_router)
app.include_router(groups_router)
app.include_router(settlements_router)
app.include_router(users_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Roommate Sync API!"}