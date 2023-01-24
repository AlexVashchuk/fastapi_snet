from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import relationship
from db.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    title = Column(String(50))
    text = Column(String(350))
    user = Column(Integer, ForeignKey("users.id"))
    user_id = relationship("User")
    date = Column(DateTime, default=datetime.now())
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    deleted_at = Column(DateTime)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    username = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String(72))


class LikeDislike(Base):
    __tablename__ = "likedislike"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), index=True)
    post = Column(Integer, ForeignKey("posts.id"), index=True)
    likedislike = Column(Boolean)
    user_id = relationship("User")
    post_id = relationship("Post")

    UniqueConstraint("user_id", "post_id", name="upx_1")
    