from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings
from datetime import datetime, timedelta

from ..Classes.token import Token
from ..models import Denuncia, Topico, Comentario, User, CategoriaForum

Token = Token()

class DenunciaTest(APITestCase):
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
        self.user2 = User.objects.create(username="XXXXXXXXX", password="testpass123", admin=False)

        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))

    def test_create_denuncia(self):
        url = reverse('denuncia-create')
        data = {
            'reported_by': self.user.id,
            'content_type': 'Topico',
            'content_id': self.topico.id,
            'reason': 'Teste Motivo'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Denuncia.objects.count(), 1)
        self.assertEqual(Denuncia.objects.get().reason, 'Teste Motivo')

    def test_list_denuncias(self):
        denuncia = {
            'reported_by': self.user.id,
            'content_type': 'Comentario',
            'content_id': self.comentario.id,
            'reason': 'Teste Motivo'
        }
        url_create = reverse('denuncia-create')
        url = reverse('denuncia-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.post(url_create, denuncia, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reason'], 'Teste Motivo')

    def test_update_status_denuncia(self):
        denuncia = {
            'reported_by': self.user.id,
            'content_type': 'Comentario',
            'content_id': self.comentario.id,
            'reason': 'Teste Motivo'
        }
        url_create = reverse('denuncia-create')
        url = reverse('update-status')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response_create = self.client.post(url_create, denuncia, format='json')
        denuncia_id = response_create.data['id']
        data = {'status': 'Resolvido',
                'denuncia_id': denuncia_id,
                'resolution': 'Teste Resolução'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Denuncia.objects.get(id=denuncia_id).status, 'Resolvido')

    def test_banned_user (self):
        
        url = reverse('banned-user') + f'?user_id={self.user2.id}'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.user2.id).is_banned, True)