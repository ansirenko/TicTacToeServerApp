from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timedelta


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_game(db: Session, game: schemas.GameCreate):
    db_game = models.Game(
        player1_id=game.player1_id,
        player2_id=game.player2_id,
        player1_score=game.player1_score,
        player2_score=game.player2_score,
        result=game.result
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def create_refresh_token(db: Session, token: str, user_id: int, expires_delta: timedelta = None):
    expires_at = datetime.now() + expires_delta if expires_delta else datetime.now() + timedelta(days=7)
    db_token = models.RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    return db_token


def revoke_refresh_token(db: Session, token: str):
    db.query(models.RefreshToken).filter(models.RefreshToken.token == token).delete()
    db.commit()


def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()


def delete_old_tokens(db: Session):
    one_day_ago = datetime.now() - timedelta(days=1)
    db.query(models.RefreshToken).filter(models.RefreshToken.expires_at < one_day_ago).delete()
    db.commit()
