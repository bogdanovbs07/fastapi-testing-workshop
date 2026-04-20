from fastapi import FastAPI
from app.routes.users import router as users_router
from app.routes.utils import router as utils_router
from app.routes.items import router as items_router

app = FastAPI(title="Testing Workshop API")

app.include_router(users_router)
app.include_router(utils_router)
app.include_router(items_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Testing Workshop API"}
