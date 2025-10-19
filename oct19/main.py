from typing import Union

import uvicorn
from fastapi import FastAPI, HTTPException

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)