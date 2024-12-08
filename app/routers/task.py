from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_tasks(db:Annotated[Session, Depends(get_db)]):
    tasks_all = db.scalars(select(Task)).all()
    return tasks_all


@router.get("/task_id")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    choice_task = db.scalars(select(Task).where(Task.id == task_id)).first()

    if choice_task is not None:

        return choice_task
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], task_create: CreateTask, user_id: int):
    try:
        tasks =  db.query(User).filter(User.id == user_id).first()

        if tasks is not None:
            db.execute(
                insert(Task).values(
                    title=task_create.title,
                    content=task_create.content,
                    priority=task_create.priority,
                    slug=slugify(task_create.title),
                    user_id=user_id
                )
            )
            db.commit()
            return {'status_code': status.HTTP_200_OK, 'transaction': 'Successful'}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)], task_update: CreateTask, task_id: int ):
    result = db.execute(
        update(Task).where(Task.id == task_id).values(
            title=task_update.title,
            content=task_update.content,
            priority=task_update.priority
        )
    )
    db.commit()
    if result.rowcount > 0:
        return {'status_code': status.HTTP_404_NOT_FOUND, 'transaction': 'Task update is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.delete("/delete")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        delete(Task).where(Task.id == task_id)
    )
    db.commit()
    if result.rowcount > 0:
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task delete is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
