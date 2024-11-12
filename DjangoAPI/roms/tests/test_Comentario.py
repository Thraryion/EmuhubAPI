from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings
from datetime import datetime, timedelta

from ..Classes.token import Token
from ..models import Comentario, LikeComentario, User, CategoriaForum, Topico

Token = Token()

class TComentarioTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass123", admin=True,)
        self.categoria = CategoriaForum.objects.create(nome="Teste Categoria")
        self.topico = Topico.objects.create(
            titulo="Teste Tópico",
            descricao="Teste Descrição",
            id_categoria=self.categoria,
            id_user=self.user
        )
        self.comentario = Comentario.objects.create(
            id_user=self.user,
            id_topico=self.topico,
            comentario="test comentario"
        )

        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))
        
    def test_create_comentario(self):
        url = reverse('comentario')
        data = {
            "id_topico": self.topico.id,
            "comentario": "Teste Comentário"
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comentario.objects.count(), 2)