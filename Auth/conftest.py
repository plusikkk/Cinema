import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from Auth.models import AuthCode

User = get_user_model()

@pytest.fixture(scope="function")
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture(scope="function")
def user_data():
    return {
        "username": "testuser",
        "email": "test@gmail.com",
        "password": "yhgfrtgTYGGBHh0988766",
        "password_check": "yhgfrtgTYGGBHh0988766",
    }

@pytest.fixture(scope="function")
def inactive_user(user_data) -> User:
    db_data = user_data.copy()
    db_data.pop('password_check', None)
    user = User.objects.create_user(**db_data)
    user.is_active = False
    user.save()
    return user

@pytest.fixture(scope="function")
def active_user(user_data) -> User:
    db_data = user_data.copy()
    db_data.pop('password_check', None)
    user = User.objects.create_user(**db_data)
    user.is_active = True
    user.save()
    return user

@pytest.fixture
def register_url():
    try:
        return reverse('register')
    except:
        return "api/auth/register/"

@pytest.fixture
def activation_code(inactive_user):
    return AuthCode.objects.create(user=inactive_user, code="123456")

@pytest.fixture
def activation_url():
    try:
        return reverse('activate')
    except:
        return "api/auth/verify/"

@pytest.fixture
def resend_url():
    try:
        return reverse('resend')
    except:
        return "api/auth/resend/"


