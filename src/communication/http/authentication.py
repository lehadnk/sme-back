from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from persistence.postgres.db import find_user_by_username
from persistence.postgres.models import User
from domain.authentication import issue_jwt_token, require_any_authentication

authentication_router = APIRouter()

class AuthenticationRequest(BaseModel):
    username: str
    password: str

@authentication_router.post("/authentication/login")
def authenticate(request: AuthenticationRequest):
    user = find_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=403, detail="Login failed")

    if not user.password == request.password:
        raise HTTPException(status_code=403, detail="Login failed")

    return {"token": issue_jwt_token(user)}

@authentication_router.get("/authentication/current")
def current(user: User = Depends(require_any_authentication)):
    return user
