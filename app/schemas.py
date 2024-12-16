from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr = None
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str
    description: str
    completed: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
