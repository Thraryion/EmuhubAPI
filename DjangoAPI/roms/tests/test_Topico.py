from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import Topico, User, CategoriaForum

class TopicoAPITests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass123")
        self.categoria = CategoriaForum.objects.create(nome="Teste Categoria")

        self.create_url = reverse('topico-create')
        self.list_url = reverse('topico-list')
        self.update_url = reverse('topico-update')
        self.delete_url = reverse('topico-delete')

    def test_create_topico(self):
        data = {
            "titulo": "Novo Tópico",
            "descricao": "Descrição do tópico",
            "id_categoria": self.categoria.id,
            "id_user": self.user.id
        }
        response = self.client.post(self.create_url, data, format='json')
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

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)

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
        response = self.client.put(self.update_url, updated_data, format='json')
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

        response = self.client.delete(self.delete_url, {"topico_id": topico.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Topico.objects.filter(id=topico.id).exists())

    def test_create_comentario(self):
        topico = Topico.objects.create(
            titulo="Tópico Para Comentar",
            descricao="Descrição Para Comentar",
            id_categoria=self.categoria,
            id_user=self.user
        )

        data = {
            "comentario": "Novo Comentário",
            "id_topico": topico.id,
            "id_user": self.user.id
        }
        response = self.client.post(reverse('comentario-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comentario"], data["comentario"])
        self.assertEqual(response.data["id_topico"], topico.id)