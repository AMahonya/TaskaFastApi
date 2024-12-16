from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from app.models import User, Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.protection import get_user_by_token

router = APIRouter(prefix="/task", tags=["task"])


@router.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), username: str = Depends(get_user_by_token)):
    user = db.query(User).filter(User.username == username).first()
    db_task = Task(**task.model_dump(), user_id=user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/tasks/", response_model=List[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.model_dump().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return task
