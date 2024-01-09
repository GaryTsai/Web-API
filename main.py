from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

key = os.getenv("FAKE_VALUE")
app = FastAPI()

origins = [
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Stock(BaseModel):
    stock_list: list

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/items/")
async def create_item(item: Stock):
    print(item)
    return item

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}