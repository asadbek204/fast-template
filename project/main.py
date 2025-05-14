import uvicorn
from fastapi import FastAPI
from routers import router
from settings import settings


app = FastAPI()
app.include_router(router)


@app.get("/")
async def home():
    return "hello"


def main():
    uvicorn.run(app=app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
