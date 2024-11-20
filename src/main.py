from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from src.api.v1 import router
from src.core.rabbit_connection import rabbit_connection


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await rabbit_connection.connect()
    await rabbit_connection.consume("your-queue-name")
    yield
    await rabbit_connection.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
