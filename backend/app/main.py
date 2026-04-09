import uvicorn
from fastapi import FastAPI

from backend.api import agent

app = FastAPI()
app.include_router(agent.router, prefix="/agent", tags=["ai模块"])

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8888)