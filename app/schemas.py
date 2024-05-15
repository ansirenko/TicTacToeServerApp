from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional

class GameBase(BaseModel):
    player1_id: int
    player2_id: int
    player1_score: int = 0
    player2_score: int = 0
    result: Optional[str] = None

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=8)

class User(UserBase):
    id: int
    wins: int = 0
    losses: int = 0
    draws: int = 0
    games: List[Game] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None