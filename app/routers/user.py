from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users_all = db.scalars(select(User)).all()
    return users_all


@router.get("/user_id")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    choice_user = db.scalars(select(User).where(User.id == user_id)).first()

    if choice_user is not None:

        return choice_user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.get("/user_id/tasks")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks_all = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks_all


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], user_create: CreateUser):
    try:
        db.execute(
            insert(User).values(
                username=user_create.username,
                firstname=user_create.firstname,
                lastname=user_create.lastname,
                age=user_create.age,
                slug=slugify(user_create.username)
            )
        )
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'
        }
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)], user_update: UpdateUser, user_id: int ):
    result = db.execute(
        update(User).where(User.id == user_id).values(
            firstname=user_update.firstname,
            lastname=user_update.lastname,
            age=user_update.age
        )
    )
    db.commit()
    if result.rowcount > 0:
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")



@router.delete("/delete")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.query(User).filter(User.id == user_id).first()

    if result:
        db.query(Task).filter(Task.user_id == user_id).delete(synchronize_session='fetch')
        db.delete(result)
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User delete is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

