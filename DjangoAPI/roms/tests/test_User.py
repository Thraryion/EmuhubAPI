from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import User
from ..Classes.token import Token
from datetime import datetime, timedelta

Token = Token()

class TestUser(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            password='123456',
            username='Admin',
            admin=True
        )
        self.user.set_password('123456') 
        self.user.save()
        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))

    def test_User_list(self):
        url = reverse('user-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_User_detail(self):
        url = reverse('user-detail')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_User_create(self):
        url = reverse('user-create')
        data = {
            'email': 'test2@example.com',
            'password': '123456',
            'username': 'XXXXX',
            'admin': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_User_update(self):
        url = reverse('user-update')
        data = {
            'email': 'test4@example.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
