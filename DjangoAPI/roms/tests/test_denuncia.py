from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings
from datetime import datetime, timedelta

from ..Classes.token import Token
from ..models import Denuncia, Topico, Comentario, User

class DenunciaTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='XXXXXXXX', password='XXXXXXXXXXXX')
        self.token = Token().create(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.topico = Topico.objects.create(titulo='Test Topico', descricao='Teste', user=self.user)
        self.denuncia = Denuncia.objects.create(topico=self.topico, user=self.user, motivo='Teste')