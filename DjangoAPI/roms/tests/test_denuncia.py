from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings
from datetime import datetime, timedelta

from ..Classes.token import Token
from ..models import Denuncia, Topico, Comentario, User