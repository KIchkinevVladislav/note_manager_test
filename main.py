import uvicorn
from fastapi import FastAPI

from app.api.user_handlers import user_routers


app = FastAPI()

app.include_router(user_routers, tags=["user"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
