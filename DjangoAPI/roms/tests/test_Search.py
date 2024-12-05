from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Topico, ROM, Categoria_Jogo, CategoriaForum, User, Emulador
from django.conf import settings
from ..Classes.token import Token
from datetime import datetime, timedelta
import jwt

Token = Token()

class SearchTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser1", password="testpass123")
        self.categoria = CategoriaForum.objects.create(nome="jogos")
        self.topico = Topico.objects.create(
            titulo="como o pikachu ganhou choque do trovao",
            descricao="sim isso ai, ficou sabendo legal",
            id_categoria=self.categoria,
            id_user=self.user,
            tags= "pokemon, nintendo"
        )
        self.categoriaJogo = Categoria_Jogo.objects.create(nome="aventura")
        self.emulador = Emulador.objects.create(
            nome="mgba",
            console="gameboy",
            empresa="nintendo"
        )
        self.rom = ROM.objects.create(
            title='pokemon emerald',
            description='Test ROM description',
            categoria=self.categoriaJogo,
            emulador=self.emulador,
        )

    def test_search(self):
        url = reverse('search-rom') + "?search=pokemon"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_categoria(self):
        url = reverse('search-topico') + "?search=jogos"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_categoria_rom(self):
        url = reverse('search-rom') + "?search=aventura"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_tags(self):
        url = reverse('search-topico') + "?search=nintendo"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
