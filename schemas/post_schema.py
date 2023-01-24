from pydantic import BaseModel
from datetime import datetime


class Likes(BaseModel):
    reaction: str
    

class LikesInDB(Likes):
    user_id: int
    post_id: int
    description: str


class Post(BaseModel):
    title: str
    text: str


class PostUpdate(BaseModel):
    title: str = None
    text: str = None


class PostOnUpdate(PostUpdate):
    date: datetime
    author_id: int
    likes: int
    dislikes: int


class PostInDB(Post):
    date: datetime
    author: str
    author_id: int
    likes: int
    dislikes: int


class PostInDBExt(PostInDB, Likes):
    pass


class PostInDBFull(PostOnUpdate):
        id: int
        deleted_at: datetime