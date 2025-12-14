from datetime import timedelta
import pytest
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.utils import timezone
from Auth.models import AuthCode
from django.core import mail

User = get_user_model()

@pytest.mark.django_db
def test_register_new_user_success(api_client, user_data, register_url) -> None:
    with patch('Auth.views.send_act_email') as mock_email:
        response = api_client.post(register_url, user_data, format='json')

        assert response.status_code == 201
        assert User.objects.count() == 1
        assert User.objects.first().email == user_data['email']
        mock_email.assert_called_once()

@pytest.mark.django_db
def test_register_existing_active_user_fail(api_client, active_user, user_data, register_url) -> None:
    response = api_client.post(register_url, user_data, format='json')

    assert response.status_code == 400
    assert "Користувач з таким email вже існує" in str(response.data)

@pytest.mark.django_db
def test_register_existing_inactive_user_resend(api_client, inactive_user, user_data, register_url) -> None:
    new_data = user_data.copy()
    new_data['password'] = "new_password---01"
    new_data['password_check'] = "new_password---01"

    with patch('Auth.views.send_act_email') as mock_email:
        response = api_client.post(register_url, new_data, format='json')

        assert response.status_code == 200
        inactive_user.refresh_from_db()
        assert inactive_user.check_password("new_password---01")
        mock_email.assert_called_once()

@pytest.mark.django_db
def test_register_email_failure_rollback(api_client, user_data, register_url) -> None:
    with patch('Auth.views.send_act_email', side_effect=Exception("SMTP ERROR")):
        response = api_client.post(register_url, user_data, format='json')

        assert response.status_code == 500
        assert "SMTP ERROR" in str(response.data)
        assert User.objects.count() == 0

@pytest.mark.django_db
def test_register_invalid_data(api_client, register_url) -> None:
    invalid_data = {
        "username": "testuser",
        "email": "invalid",
    }

    response = api_client.post(register_url, invalid_data, format='json')

    assert response.status_code == 400
    assert User.objects.count() == 0

@pytest.mark.django_db
def test_register_existing_email_failure(api_client, active_user, register_url) -> None:
    data = {
        "username": "new_unique_name",
        "email": "test@gmail.com",
        "password": "PassWord123-----kkmfirm",
        "password_check": "PassWord123-----kkmfirm"
    }
    response = api_client.post(register_url, data, format='json')

    assert response.status_code == 400
    assert "Користувач з таким email вже існує" in str(response.data)

@pytest.mark.django_db
def test_activation_success(api_client, inactive_user, activation_code, activation_url):
    data = {
        "email": inactive_user.email,
        "code": "123456"
    }
    response = api_client.post(activation_url, data, format='json')

    assert response.status_code == 200
    assert "access" in response.data

    inactive_user.refresh_from_db()
    assert inactive_user.is_active is True
    assert AuthCode.objects.count() == 0

@pytest.mark.django_db
def test_activation_invalid_code(api_client, inactive_user, activation_code, activation_url):
    data = {
        "email": inactive_user.email,
        "code": "000000"
    }
    response = api_client.post(activation_url, data, format='json')

    assert response.status_code == 400
    assert "Invalid code" in str(response.data)

    inactive_user.refresh_from_db()
    assert inactive_user.is_active is False

@pytest.mark.django_db
def test_activation_expired_code(api_client, inactive_user, activation_code, activation_url):
    past_time = timezone.now() - timedelta(minutes=10)
    AuthCode.objects.filter(id=activation_code.id).update(created_at=past_time)

    data = {
        "email": inactive_user.email,
        "code": "123456"
    }
    response = api_client.post(activation_url, data, format='json')

    assert response.status_code == 400
    assert "Code has expired" in str(response.data)

@pytest.mark.django_db
def test_activation_user_not_found(api_client, activation_url):
    data = {
        "email": "email@gmail.com",
        "code": "123456"
    }
    response = api_client.post(activation_url, data, format='json')
    assert response.status_code == 404

@pytest.mark.django_db
def test_activation_missing_data(api_client, activation_url):
    response = api_client.post(activation_url, {}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_resend_code_success(api_client, inactive_user, resend_url):
    data = {"email": inactive_user.email}

    with patch('Auth.views.send_act_email') as mock_email:
        response = api_client.post(resend_url, data, format='json')

        assert response.status_code == 200
        assert "New code sent" in str(response.data)
        mock_email.assert_called_once()

@pytest.mark.django_db
def test_resend_code_already_active(api_client, active_user, resend_url):
    data = {"email": active_user.email}

    response = api_client.post(resend_url, data, format='json')

    assert response.status_code == 400
    assert "Account has already active" in str(response.data)

@pytest.mark.django_db
def test_resend_code_user_not_found(api_client, resend_url):
    data = {"email": "email@gmail.com"}
    response = api_client.post(resend_url, data, format='json')
    assert response.status_code == 404

@pytest.mark.django_db
def test_resend_code_overwrites_existing_valid_code(api_client, inactive_user, activation_code, resend_url, activation_url):
    old_code_value = activation_code.code
    assert old_code_value == "123456"

    response = api_client.post(resend_url, {"email": inactive_user.email}, format='json')

    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [inactive_user.email]

    activation_code.refresh_from_db()
    new_code_value = activation_code.code

    assert new_code_value != old_code_value
    assert new_code_value != "123456"

    response_fail = api_client.post(activation_url, {"email": inactive_user.email, "code": old_code_value}, format='json')
    assert response_fail.status_code == 400

    response_success = api_client.post(activation_url, {"email": inactive_user.email, "code": new_code_value}, format='json')
    assert response_success.status_code == 200

    assert inactive_user.is_active is False
    inactive_user.refresh_from_db()
    assert inactive_user.is_active is True

