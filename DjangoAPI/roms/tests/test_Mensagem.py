from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Emulador, User
from django.conf import settings
from ..Classes.token import Token
from datetime import datetime, timedelta
import jwt

Token = Token()