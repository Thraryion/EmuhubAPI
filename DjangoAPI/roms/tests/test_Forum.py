from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User, Comunidade, Topico, Categoria_Forum, LikeTopico, LikeComentario, Comentario
from django.conf import settings
import jwt

class ForumTest(APITestCase):
    def setUp(self):

        self.user = User.objects.create(
                username='joao',
                email='test@example.com',
                password='123',
                admin=True,
            )
        self.user.save()
        self.topico = Topico.objects.create(
            titulo='Teste',
            descricao='Teste',
            id_user=self.user,
            id_categoria=Categoria_Forum.objects.create(nome='Teste')
        )
        self.topico.save()
        self.comentario = Comentario.objects.create(
            descricao='Teste',
            id_topico=self.topico,
            id_user=self.user
        )

    def test_create_topico(self):
        url = reverse('topico-create')
        data = {
            'titulo': 'Teste',
            'descricao': 'Teste',
            'id_user': self.user.id,
            'id_categoria': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    