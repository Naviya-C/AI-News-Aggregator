from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    second_name: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True