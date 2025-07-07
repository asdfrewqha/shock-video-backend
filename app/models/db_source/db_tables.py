from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.config import DEFAULT_AVATAR_URL
from app.models.auth_schemas import Role


Base = declarative_base()


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    comment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
    )
    liked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "comment_id", name="like_user_comment_uc"),)


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    video_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("videos.id", ondelete="CASCADE"))
    liked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "video_id", name="like_user_video_uc"),)


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscriber_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    subscribed_to_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    subscribed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class View(Base):
    __tablename__ = "views"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    video_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("videos.id", ondelete="CASCADE"))
    viewed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    user_username: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parent_username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    likes: Mapped[int] = mapped_column(default=0, nullable=False)
    dislikes: Mapped[int] = mapped_column(default=0, nullable=False)
    replies_count: Mapped[int] = mapped_column(default=0, nullable=False)

    user = relationship("User", back_populates="comments")
    video = relationship("Video", back_populates="comment_list")
    comm_likers = relationship("CommentLike", backref="comment", cascade="all, delete")

    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side=[id],
        backref="replies",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)
    avatar_url: Mapped[str] = mapped_column(String, nullable=False, default=DEFAULT_AVATAR_URL)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    followers_count: Mapped[int] = mapped_column(default=0, nullable=False)
    subscriptions_count: Mapped[int] = mapped_column(default=0, nullable=False)

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
    videos = relationship("Video", back_populates="author", cascade="all, delete")


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    views: Mapped[int] = mapped_column(default=0)
    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)
    comments: Mapped[int] = mapped_column(default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    author = relationship("User", back_populates="videos")
    likers = relationship("Like", backref="video", cascade="all, delete")
    comment_list = relationship("Comment", back_populates="video", cascade="all, delete")
