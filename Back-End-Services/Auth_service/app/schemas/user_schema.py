from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str 
    username:str
    email: EmailStr  
    password: str
    
class UserLogin(BaseModel):
    identifier: str
    password: str
 
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    
    class Config:
        from_attributes = True 