from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(request)

@router.post("/login", response_model=TokenResponse)
def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(request)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
