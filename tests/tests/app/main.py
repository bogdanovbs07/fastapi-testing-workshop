from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

app = FastAPI(title="Testing Workshop API")

# Models
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserResponse(User):
    id: int

class Item(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    tax: Optional[float] = None

class ItemResponse(Item):
    id: int

# In-memory storage
users_db = []
items_db = []
user_counter = 0
item_counter = 0

@app.get("/")
async def root():
    return {"message": "Welcome to Testing Workshop API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: User):
    global user_counter
    user_counter += 1
    user_dict = user.dict()
    user_dict["id"] = user_counter
    users_db.append(user_dict)
    return user_dict

@app.get("/users/", response_model=List[UserResponse])
async def get_users():
    return users_db

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(item: Item):
    global item_counter
    item_counter += 1
    item_dict = item.dict()
    item_dict["id"] = item_counter
    items_db.append(item_dict)
    return item_dict

@app.get("/items/", response_model=List[ItemResponse])
async def get_items():
    return items_db
