from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, request: UserRegisterRequest) -> TokenResponse:
        existing = self.user_repo.get_by_email(request.email)
        if existing:
            raise BadRequestException("User with this email already exists")
        
        hashed_pwd = get_password_hash(request.password)
        new_user = User(
            email=request.email.lower(),
            password_hash=hashed_pwd,
            full_name=request.full_name,
            phone=request.phone,
            role=UserRole.USER
        )
        saved_user = self.user_repo.create(new_user)
        token = create_access_token(subject=saved_user.id, role=saved_user.role.value)
        return TokenResponse(
            access_token=token,
            role=saved_user.role.value,
            user_id=saved_user.id,
            full_name=saved_user.full_name
        )

    def login(self, request: UserLoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        
        token = create_access_token(subject=user.id, role=user.role.value)
        return TokenResponse(
            access_token=token,
            role=user.role.value,
            user_id=user.id,
            full_name=user.full_name
        )
