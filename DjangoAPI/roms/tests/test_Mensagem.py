# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from ..models import User, Conversa, Mensagem
# from django.conf import settings
# from ..Classes.token import Token
# from datetime import datetime, timedelta
# import jwt

# Token = Token()

# class MensagensPrivadas(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create(username='user1', password='123')
#         self.user2 = User.objects.create(username='user2', password='123')
#         self.token = Token.create_token(self.user.id, self.user.admin, datetime.utcnow() + timedelta(minutes=60))
#         self.Conversa = Conversa.objects.create(id_user1=self.user, id_user2=self.user2)

#     def test_enviar_mensagem(self):
#         url = reverse('mensagem-create')
#         data ={
#             'id_conversa': self.Conversa.id,
#             'mensagem': 'Olá, como você está?',
#         }
#         response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['mensagem'], 'Olá, como você está?')
    
#     def test_enviar_mensagem_nao_autorizado(self):
#         url = reverse('mensagem-create')
#         data ={
#             'id_conversa': self.Conversa.id,
#             'mensagem': 'Olá, como você está?',
#         }
#         response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer 1458156')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_create_conversa(self):
#         url = reverse('conversa-create')
#         data ={
#             'id_user2': self.user2.id,
#         }
#         response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
