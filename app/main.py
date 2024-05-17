from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import uvicorn
from datetime import timedelta, datetime

from app import models, schemas, crud, database, auth
from app.auth import validate_email, validate_password, get_password_hash
from app.exceptions import EmailAlreadyRegisteredException, UserAlreadyExistsException

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


@app.post("/register/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    validate_email(user.email)

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise EmailAlreadyRegisteredException()

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise UserAlreadyExistsException()

    validate_password(user.password)

    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    crud.create_refresh_token(db=db, token=refresh_token, user_id=user.id, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/token/refresh", response_model=schemas.Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(database.get_db)):
    token = crud.get_refresh_token(db, token=refresh_token)
    if not token or token.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user(db, user_id=token.user_id)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return schemas.User.from_orm(current_user)


@app.post("/logout")
def logout(db: Session = Depends(database.get_db), token: str = Depends(auth.oauth2_scheme)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        jti = payload.get("jti")
        if jti:
            crud.delete_old_tokens(db)
            crud.revoke_refresh_token(db, token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"msg": "Successfully logged out"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
