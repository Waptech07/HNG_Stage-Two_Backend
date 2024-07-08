import pytest # type: ignore
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User, Organisation


@pytest.mark.django_db
class TestAuth:
    client = APIClient()

    def test_register_user_with_default_organisation(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        print(response.data)
        assert response.data['status'] == 'success'
        assert 'accessToken' in response.data['data']
        assert Organisation.objects.count(), 1
        assert Organisation.objects.first().name, "John's Organisation"

    def test_login_user_successfully(self):
        # Register the user first
        self.test_register_user_with_default_organisation()
        url = reverse('login')
        data = {
            "email": "john@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'accessToken' in response.data['data']

    def test_fail_if_required_fields_missing(self):
        url = reverse('register')

        # Missing firstName
        data = {
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing lastName
        data = {
            "firstName": "John",
            "email": "john@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing email
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing password
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_fail_if_duplicate_email(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        # Attempt to register another user with the same email
        data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password123",
            "phone": "0987654321"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
