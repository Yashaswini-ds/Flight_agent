import pytest
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.core.security import verify_password, decode_access_token
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.models.user import UserRole

def test_user_registration(db_session):
    service = AuthService(db_session)
    req = UserRegisterRequest(
        email="newuser@flightagent.com",
        password="securepassword",
        full_name="Jane Doe",
        phone="+919876543210"
    )
    res = service.register(req)

    assert res.access_token is not None
    assert res.role == "USER"
    assert res.full_name == "Jane Doe"

    payload = decode_access_token(res.access_token)
    assert payload["sub"] == res.user_id
    assert payload["role"] == "USER"

def test_user_duplicate_registration_fails(seeded_db):
    service = AuthService(seeded_db)
    req = UserRegisterRequest(
        email="testuser@flightagent.com",
        password="password123",
        full_name="Duplicate User"
    )
    with pytest.raises(BadRequestException):
        service.register(req)

def test_user_login_success(seeded_db):
    service = AuthService(seeded_db)
    req = UserLoginRequest(
        email="testuser@flightagent.com",
        password="password123"
    )
    res = service.login(req)

    assert res.access_token is not None
    assert res.role == "USER"

def test_user_login_invalid_password(seeded_db):
    service = AuthService(seeded_db)
    req = UserLoginRequest(
        email="testuser@flightagent.com",
        password="wrongpassword"
    )
    with pytest.raises(UnauthorizedException):
        service.login(req)

def test_admin_login(seeded_db):
    service = AuthService(seeded_db)
    req = UserLoginRequest(
        email="testadmin@flightagent.com",
        password="adminpass123"
    )
    res = service.login(req)

    assert res.role == "ADMIN"
    payload = decode_access_token(res.access_token)
    assert payload["role"] == "ADMIN"
