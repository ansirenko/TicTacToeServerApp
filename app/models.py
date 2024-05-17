from datetime import datetime

from sqlalchemy import Column, Integer, String, MetaData, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)

    games = relationship(
        "Game", primaryjoin="or_(User.id==Game.player1_id, User.id==Game.player2_id)", overlaps="player1,player2")
    refresh_tokens = relationship("RefreshToken", back_populates="owner")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"))
    player1_score = Column(Integer)
    player2_score = Column(Integer)
    result = Column(String(50))

    player1 = relationship("User", foreign_keys=[player1_id], overlaps="games")
    player2 = relationship("User", foreign_keys=[player2_id], overlaps="games")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime)

    owner = relationship("User", back_populates="refresh_tokens")
