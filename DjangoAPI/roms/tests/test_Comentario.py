from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings
from datetime import datetime, timedelta

from ..Classes.token import Token
from ..models import Comentario, LikeComentario, User, CategoriaForum, Topico

Token = Token()

class ComentarioTests(APITestCase):
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
            descricao="test comentario"
        )

        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))
        
    def test_create_comentario(self):
        url = reverse('comentario-create')
        data = {
            "id_topico": self.topico.id,
            "descricao": "test comentario 2"
            
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comentario.objects.count(), 2)

    def test_update_comentario(self):
        url = reverse('comentario-update')
        data = {
            "id": self.comentario.id,
            "id_topico": self.topico.id,
            "descricao": "test comentario 3"
        }
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comentario.refresh_from_db()
        self.assertEqual(self.comentario.descricao, "test comentario 3")

    def test_delete_comentario(self):
        url = reverse('comentario-delete')
        data = {
            "id": self.comentario.id
        }
        response = self.client.delete(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comentario.objects.count(), 0)

    def test_list_comentario(self):
        url = reverse('comentario-list') + f'?id_topico={self.topico.id}&id_user={self.user.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_like_comentario(self):
        url = reverse('comentario-like')
        data = {
            "id": self.comentario.id
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LikeComentario.objects.count(), 1)

    def test_unlike_comentario(self):
        like = LikeComentario.objects.create(id_user=self.user, id_comentario=self.comentario)
        url = reverse('comentario-unlike')
        data = {
            "id": self.comentario.id
        }
        response = self.client.delete(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LikeComentario.objects.count(), 0)

    def test_isHelpful_comentario(self):
        url = reverse('comentario-is-helpful')
        data = {
            "id": self.comentario.id
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comentario.refresh_from_db()
        self.assertEqual(self.comentario.is_helpful, True)