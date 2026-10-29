import pytest
from app.services.admin_service import AdminService
from app.api.deps import get_current_admin
from app.models.user import User, UserRole
from app.core.exceptions import ForbiddenException

def test_user_cannot_access_admin_privileges():
    normal_user = User(id="u1", email="u@test.com", password_hash="x", full_name="User", role=UserRole.USER)
    
    with pytest.raises(ForbiddenException):
        get_current_admin(current_user=normal_user)

def test_admin_access_allowed():
    admin_user = User(id="a1", email="a@test.com", password_hash="x", full_name="Admin", role=UserRole.ADMIN)
    
    verified = get_current_admin(current_user=admin_user)
    assert verified.id == "a1"
    assert verified.role == UserRole.ADMIN

def test_admin_dashboard_overview(seeded_db):
    service = AdminService(seeded_db)
    overview = service.get_dashboard_overview()

    assert "total_users" in overview
    assert "total_flights" in overview
    assert "total_bookings" in overview
    assert overview["total_users"] >= 2
    assert overview["total_flights"] >= 1

def test_admin_list_users(seeded_db):
    service = AdminService(seeded_db)
    users = service.list_all_users()

    assert len(users) >= 2
    roles = [u.role for u in users]
    assert UserRole.USER in roles
    assert UserRole.ADMIN in roles
