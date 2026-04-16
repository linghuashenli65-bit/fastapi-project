import uvicorn
from fastapi import FastAPI
from sqlalchemy.sql.functions import user

from backend.api import agent
from backend.api import student
from backend.api import teacher
from backend.api import class_student
from backend.api import employment
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="学生管理系统",version="0.1",prefix="/api/v1")
app.include_router(agent.router, prefix="/agent", tags=["ai模块"])
app.include_router(student.router, prefix="/student", tags=["学生模块"])
app.include_router(teacher.router,prefix="/teacher",tags=["教师模块"])
app.include_router(class_student.router,prefix="/class",tags=["班级模块"])
app.include_router(
    employment.router,
    prefix="/employment",
    tags=["就业模块"]
)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8888)