import uvicorn
from fastapi import FastAPI

from app.api.notes_handlers import note_routers
from app.api.user_handlers import user_routers

app = FastAPI()

app.include_router(user_routers, prefix="/users", tags=["users"])
app.include_router(note_routers, prefix="/notes", tags=["notes"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
