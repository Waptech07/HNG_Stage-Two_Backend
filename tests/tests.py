import pytest # type: ignore
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User, Organisation
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.conf import settings
import jwt

@pytest.mark.django_db
class TestAuth:
    client = APIClient()

    def test_user_registration(self):
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
        assert 'accessToken' in response.data['data']

    def test_login(self):
        # Register the user first
        self.test_user_registration()
        url = reverse('login')
        data = {
            "email": "john@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'accessToken' in response.data['data']
        token = response.data['data']['accessToken']

        # Decode the token to verify its contents
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print(decoded_token)
        assert decoded_token['userId'] == response.data['data']['user']['userId']
        # Allow a small buffer to avoid timing issues
        assert decoded_token['exp'] > datetime.timestamp(make_aware(datetime.now())) - 1

    def test_token_expiry(self):
        # Register and login to get the token
        self.test_user_registration()
        url = reverse('login')
        data = {
            "email": "john@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        token = response.data['data']['accessToken']

        # Verify token expiry
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expiry = make_aware(datetime.fromtimestamp(decoded_token['exp']))
        expected_expiry = make_aware(datetime.now()) + timedelta(minutes=60)
        assert abs((expiry - expected_expiry).total_seconds()) < 3600

    def test_unauthorized_organisation_access(self):
        # Register and login user 1
        self.test_user_registration()
        url = reverse('login')
        data = {
            "email": "john@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        token = response.data['data']['accessToken']

        # Create organisation with user 1
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        org_url = reverse('organisation-list-create')
        org_data = {
            "name": "Test Organisation",
            "description": "Test Description"
        }
        response = self.client.post(org_url, org_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        org_id = response.data['data']['orgId']

        # Register and login user 2
        url = reverse('register')
        data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        self.client.post(url, data, format='json')
        url = reverse('login')
        data = {
            "email": "jane@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        token = response.data['data']['accessToken']

        # Attempt to access organisation with user 2
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        org_detail_url = reverse('organisation-detail', args=[org_id])
        response = self.client.get(org_detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
