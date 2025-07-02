import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.config import DEFAULT_AVATAR_URL
from app.models.auth_schemas import Role


Base = declarative_base()


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    comment_id = Column(Uuid, ForeignKey("comments.id", ondelete="CASCADE"))
    liked_at = Column(DateTime, server_default=func.now())
    like = Column(Boolean, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "comment_id", name="like_user_comment_uc"),)


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    video_id = Column(Uuid, ForeignKey("videos.id", ondelete="CASCADE"))
    liked_at = Column(DateTime, server_default=func.now())
    like = Column(Boolean, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "video_id", name="like_user_video_uc"),)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscriber_id = Column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )
    subscribed_to_id = Column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )
    subscriped_at = Column(DateTime, server_default=func.now())


class View(Base):
    __tablename__ = "views"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    video_id = Column(Uuid, ForeignKey("videos.id", ondelete="CASCADE"))
    viewed_at = Column(DateTime, server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    likes = Column(Integer, nullable=False, default=0)
    dislikes = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="comments")
    video = relationship("Video", back_populates="comment_list")
    comm_likers = relationship("CommentLike", backref="comment", cascade="all, delete")

    parent: Mapped["Comment"] = relationship("Comment", remote_side=[id], backref="replies")


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String(100), nullable=False, unique=False)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String(100), unique=False, nullable=False)
    role = Column(Enum(Role), default=Role.USER)
    avatar_url = Column(String, nullable=False, default=DEFAULT_AVATAR_URL)
    description = Column(Text, nullable=False, default="")
    followers_count = Column(Integer, nullable=False, default=0)
    subscriptions_count = Column(Integer, nullable=False, default=0)

    liked_videos = relationship("Like", backref="user", cascade="all, delete")
    viewed_videos = relationship("View", backref="user", cascade="all, delete")
    subscriptions = relationship(
        "User",
        secondary="subscriptions",
        primaryjoin=id == Subscription.subscriber_id,
        secondaryjoin=id == Subscription.subscribed_to_id,
        backref="subscribers",
    )
    comments = relationship("Comment", back_populates="user", cascade="all, delete")
    liked_comments = relationship("CommentLike", backref="user", cascade="all, delete")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Uuid, primary_key=True, unique=True)
    author_id = Column(Uuid, nullable=False)
    url = Column(String, unique=True, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    description = Column(Text, nullable=True, default="")

    likers = relationship("Like", backref="video", cascade="all, delete")
    comment_list = relationship("Comment", back_populates="video", cascade="all, delete")
