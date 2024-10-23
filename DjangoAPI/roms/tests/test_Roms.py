from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import ROM, Categoria_Jogo, Emulador, User
from django.conf import settings
import jwt

class RomsTests(APITestCase):
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
            categoria=1,
            emulador=1,
        )

    def _generate_token(self):
        token = jwt.encode(
            {'user_id': self.user.id,
            'admin': self.user.admin},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        return token

    def test_list_roms(self):
        url = reverse('rom-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_rom(self):
        token = self._generate_token()
        url = reverse('rom-create')
        data = {
            'title': 'Test ROM 2',
            'description': 'Test ROM description 2',
            'id_categoria': 1,
            'id_emulador': 1,
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ROM.objects.count(), 2)

    def test_retrieve_rom(self):
        url = reverse('rom-detail', args=[self.rom.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test ROM')

    def test_update_rom(self):
        token = self._generate_token()
        url = reverse('rom-detail', args=[self.rom.id])
        data = {
            'title': 'Test ROM Updated',
            'description': 'Test ROM description Updated',
            'id_categoria': 1,
            'id_emulador': 1,
        }
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rom.refresh_from_db()
        self.assertEqual(self.rom.title, 'Test ROM Updated')

    def test_delete_rom(self):
        token = self._generate_token()
        url = reverse('rom-detail', args=[self.rom.id])
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ROM.objects.count(), 0)


    