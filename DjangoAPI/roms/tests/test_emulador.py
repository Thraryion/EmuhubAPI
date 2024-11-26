from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Emulador, User
from django.conf import settings
from ..Classes.token import Token
from datetime import datetime, timedelta
import jwt

Token = Token()

class EmuladorTests(APITestCase):
    def setUp(self):
        self.emulador = Emulador.objects.create(
            nome="Teste",
            console="Teste",
            empresa="Teste"
        )
        self.emulador.save()
        self.user = User.objects.create(
            username='joao',
            email='test@example.com',
            password='123',
            admin=True,
        )
        self.user.set_password('123456') 
        self.user.save()
        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))

    def test_get_emuladores(self):
        url = reverse('emuladores')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_emulador(self):
        url = reverse('emulador-create')
        data = {
            "nome": "Teste 2",
            "console": "Teste 2",
            "empresa": "Teste 2"
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_emulador(self):
        url = reverse('emulador-update')
        data = {
            "id": self.emulador.id,
            "nome": "Teste 3",
            "console": "Teste 3",
            "empresa": "Teste post3"
        }
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.emulador.refresh_from_db()
        self.assertEqual(self.emulador.nome, "Teste 3")

    def test_delete_emulador(self):
        url = reverse('emulador-delete')
        data = {
            "emulador_id": self.emulador.id
        }
        response = self.client.delete(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
