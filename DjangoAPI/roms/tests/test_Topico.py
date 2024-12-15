from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import Topico, User, CategoriaForum, LikeTopico
from ..Classes.token import Token
from datetime import datetime, timedelta

Token = Token()

class TopicoAPITests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass123", admin=True,)
        self.categoria = CategoriaForum.objects.create(nome="Teste Categoria")
        self.topico = Topico.objects.create(
            titulo="Teste Tópico",
            descricao="Teste Descrição",
            id_categoria=self.categoria,
            id_user=self.user
        )
        self.like = LikeTopico.objects.create(
            id_topico=self.topico,
            id_user=self.user
        )

        self.create_url = reverse('topico-create')
        self.list_url = reverse('topico-list')
        self.update_url = reverse('topico-update')
        self.delete_url = reverse('topico-delete')

        self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))

    def test_create_topico(self):
        data = {
            "titulo": "Novo Tópico",
            "descricao": "Descrição do tópico",
            "id_categoria": self.categoria.id,
        }
        response = self.client.post(self.create_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["titulo"], data["titulo"])
        self.assertEqual(response.data["descricao"], data["descricao"])

    def test_list_topicos(self):
        for i in range(15):
            Topico.objects.create(
                titulo=f"Tópico {i}",
                descricao=f"Descrição {i}",
                id_categoria=self.categoria,
                id_user=self.user
            )
        url = reverse('topico-list') + f"?id_user={self.user.id}"
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_topico(self):
        topico = Topico.objects.create(
            titulo="Tópico Antigo",
            descricao="Descrição Antiga",
            id_categoria=self.categoria,
            id_user=self.user             
        )

        updated_data = {
            "topico_id": topico.id,
            "titulo": "Tópico Atualizado",
            "descricao": "Descrição Atualizada",
            "id_categoria": self.categoria.id,
            "id_user": self.user.id 
        }
        response = self.client.put(self.update_url, updated_data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], updated_data["titulo"])
        self.assertEqual(response.data["descricao"], updated_data["descricao"])


    def test_delete_topico(self):
        topico = Topico.objects.create(
            titulo="Tópico Para Excluir",
            descricao="Descrição Para Excluir",
            id_categoria=self.categoria,
            id_user=self.user
        )

        response = self.client.delete(self.delete_url, {"topico_id": topico.id}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Topico.objects.filter(id=topico.id, topico_delete=True).exists())

    def test_like_topico(self):
        url_unlike = reverse('topico-unlike') + f"?topico_id={self.topico.id}"
        self.client.delete(url_unlike, HTTP_AUTHORIZATION=f'Bearer {self.token}')

        url = reverse('topico-like')
        data = {
            "id_topico": self.topico.id,
        }

        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(LikeTopico.objects.filter(id_topico=self.topico.id, id_user=self.user).exists())

    def test_unlike_topico(self):
        url = reverse('topico-unlike') + f"?topico_id={self.topico.id}"

        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LikeTopico.objects.filter(id_topico=self.topico.id, id_user=self.user).exists())

    def test_list_categoria(self):
        response = self.client.get(reverse('topico-categorias'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_topico_detail(self):
        url = reverse('topico-detail') + f"?topico_id={self.topico.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], self.topico.titulo)
        self.assertEqual(response.data["descricao"], self.topico.descricao)
