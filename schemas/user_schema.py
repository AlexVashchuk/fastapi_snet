from pydantic import BaseModel


class User(BaseModel):
    username: str
    

class UserInDB(User):  
    id: int
    is_active: bool


class UserToDB(User):      
    password: str
    repeat: str