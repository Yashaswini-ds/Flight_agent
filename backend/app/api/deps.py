from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.core.exceptions import UnauthorizedException, ForbiddenException

security_scheme = HTTPBearer()

security_scheme_optional = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired access token")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token missing subject claim")
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User no longer exists")
    return user

def get_current_user_or_demo(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme_optional),
    db: Session = Depends(get_db)
) -> User:
    user_repo = UserRepository(db)
    if credentials and credentials.credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and payload.get("sub"):
            user = user_repo.get_by_id(payload.get("sub"))
            if user:
                return user
    
    # Fallback to demo user for guest assistant chat
    demo_user = user_repo.get_by_email("user@flightagent.com")
    if demo_user:
        return demo_user
    
    first_user = db.query(User).first()
    if first_user:
        return first_user

    raise UnauthorizedException("No active user available")

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Administrator privileges required for this resource")
    return current_user
