from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config import DEFAULT_AVATAR_URL
from models.schemas.auth_schemas import Role


Base = declarative_base()


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"))
    video_id = Column(Uuid, ForeignKey("videos.id", ondelete="CASCADE"))
    liked_at = Column(DateTime, server_default=func.now())
    like = Column(Boolean, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "video_id", name="like_user_video_uc"),)


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String(100), nullable=False, unique=False)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String(100), unique=False, nullable=False)
    role = Column(Enum(Role), default=Role.USER)
    avatar_url = Column(String, nullable=False, default=DEFAULT_AVATAR_URL)

    liked_videos = relationship("Like", backref="user", cascade="all, delete")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Uuid, primary_key=True, unique=True)
    author_id = Column(Uuid, nullable=False)
    url = Column(String, unique=True, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    description = Column(String, nullable=True, default="")

    likers = relationship("Like", backref="video", cascade="all, delete")
