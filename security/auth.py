from bcrypt import checkpw, hashpw, gensalt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db.crud import user_by_username
from schemas.user_schema import User, UserInDB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logged_or_not = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def gen_hash(password: str):
    return hashpw(password.encode(), gensalt()).decode()


def check_hash(password: str, hashed_password):
    return checkpw(password.encode(), hashed_password.encode())


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = user_by_username(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserInDB(**{'id': user.id, 'username': user.username, 'is_active': user.is_active})


async def get_no_user(token: str = Depends(logged_or_not)):
    if token:
        raise HTTPException(
            status_code=400, detail="You must logout before register new user")
    return None


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_read_mode(token: str = Depends(logged_or_not)) -> int: 
    if token:
        user = user_by_username(token)
        return UserInDB(**{'id': user.id, 'username': user.username, 'is_active': user.is_active})
    return None


