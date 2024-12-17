from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import User, Categoria_Jogo, Emulador, ROM
from datetime import datetime, timedelta
from ..Classes.token import Token

Token = Token()

class TestWishlist(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='joao',
            email='test@example.com',
            password='123',
            admin=True,
        )
        self.categoria = Categoria_Jogo.objects.create(
            nome='Test Category',
        )
        self.emulador = Emulador.objects.create(
            nome='Test Emulator',
            console='Test Console',
            empresa='Test Manufacturer',
        )
        self.rom = ROM.objects.create(
            title='Test ROM',
            description='Test ROM description',
            categoria=self.categoria,
            emulador=self.emulador,
        )
        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))

    def test_add_wishlist(self):
        url = reverse('user-add-wishlist')
        data = {
            'rom_id': self.rom.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_wishlist(self):
        url = reverse('user-remove-wishlist')
        data = {
            'rom_id': self.rom.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_wishlist(self):
        url_add = reverse('user-add-wishlist')
        data = {
            'rom_id': self.rom.id,
        }
        url = reverse('user-wishlist')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response_add = self.client.post(url_add, data, format='json')
        response = self.client.get(url, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
