from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Emulador
from django.conf import settings
import jwt

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

    def _generate_token(self):
        token = jwt.encode(
            {'user_id': self.user.id,
            'admin': self.user.admin},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        return token

    def test_get_emuladores(self):
        url = reverse('emulador-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_emulador(self):
        token = self._generate_token()
        url = reverse('emulador-create')
        data = {
            "nome": "Teste 2",
            "console": "Teste 2",
            "empresa": "Teste 2"
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Emulador.objects.count(), 2)

    def test_update_emulador(self):
        url = reverse('emulador-update')
        token = self._generate_token()
        data = {
            "id": self.emulador.id,
            "nome": "Teste 3",
            "console": "Teste 3",
            "empresa": "Teste 3"
        }
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.emulador.refresh_from_db()
        self.assertEqual(self.emulador.nome, "Teste 3")

    def test_delete_emulador(self):
        url = reverse('emulador-delete')
        data = {
            "id": self.emulador.id
        }
        token = self._generate_token()
        response = self.client.delete(url, data, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_emulador_download(self):
        url = reverse('emulador-download')
        data = {
            "id": self.emulador.id
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    