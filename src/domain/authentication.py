
import jwt
from fastapi import HTTPException, Request

from config import jwt_secret
from persistence.postgres.models import User, UserRole


def issue_jwt_token(user: User) -> str:
    return jwt.encode({"id": user.id, "username": user.username, "role": user.role}, jwt_secret, algorithm="HS256")

def exchange_jwt_token(token: str):
    return User(**jwt.decode(token, jwt_secret, algorithms=['HS256']))

def require_any_authentication(request: Request) -> User:
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    if auth_token.startswith("Bearer "):
        auth_token = auth_token[len("Bearer "):]

    try:
        return exchange_jwt_token(auth_token)
    except:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

def require_admin_authentication(request: Request) -> User:
    user = require_any_authentication(request)
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="You are not allowed to access this resource")

    return user

def require_researcher_authentication(request: Request) -> User:
    user = require_any_authentication(request)
    if user.role != UserRole.researcher:
        raise HTTPException(status_code=403, detail="You are not allowed to access this resource")

    return user

def require_user_authentication(request: Request) -> User:
    user = require_any_authentication(request)
    if user.role != UserRole.user:
        raise HTTPException(status_code=403, detail="You are not allowed to access this resource")

    return user