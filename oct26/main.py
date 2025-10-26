from typing import Union

import time
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, Request
from request_models import User
from response_models import Success

app = FastAPI()


@app.get("/", tags=["根路径"])
def read_root():
    return {"Hello": "nihao"}


@app.get("/items/{item_id}", tags=["获取id"])
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/search", tags=["搜索"])
async def search(query: str, ids: int):
    if ids == 10:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"query": query, "ids": ids}

@app.post("/get-json", tags=["接收JSON"])
async def get_json(request: Request):
    print(request.headers)
    print(await request.body())
    print(await request.json())
    print(type(await request.json()))


@app.post("/get-user", tags=["get user"])
async def get_user(request: Request, user: User):
    print(user.id)
    print(user.name)
    return {"status": True}

@app.post("/get-user-response", tags=["get user"], response_model=Success)
async def get_user(request: Request, user: User):
    print(user.id)
    print(user.name)
    return {"data": user.id}


@app.post("/spend-time/{num}")
async def spend_time(request: Request, num: int):
    time.sleep(10)
    return {"num": num}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)