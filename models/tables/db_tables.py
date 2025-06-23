from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.schemas.auth_schemas import Role

Base = declarative_base()


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"))
    liked_at = Column(DateTime, server_default=func.now())
    like = Column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="like_user_video_uc"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), unique=False, nullable=False)
    role = Column(Enum(Role), default=Role.USER)

    liked_videos = relationship("Like", backref="user", cascade="all, delete")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, unique=True)
    author_id = Column(Integer, nullable=False)
    url = Column(String, unique=True, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    description = Column(String, nullable=True, default="")

    likers = relationship("Like", backref="video", cascade="all, delete")
