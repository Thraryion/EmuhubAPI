from django.shortcuts import render
from rest_framework import generics
from django.http import HttpResponse, FileResponse, Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.storage import default_storage


import base64
import jwt
from datetime import datetime, timedelta

from .Classes.wishlist import Wishlist
from .Classes.Roms import Roms
from .Classes.Auth import Auth
from .Classes.token import Token
from .models import ROM, User, Emulador, Categoria_Jogo
from .serializer import ROMSerializer, UserSerializer, EmuladorSerializer, CategoriaJogoSerializer

import base64
import logging

from django.core.files.storage import default_storage
from django.http import JsonResponse, Http404
from rest_framework import status, generics
from rest_framework.response import Response
from adrf.views import APIView
from rest_framework.exceptions import NotFound

from .models import ROM
from .Classes.token import Token

logger = logging.getLogger(__name__)

Auth = Auth()
Token = Token()
Roms = Roms()
Wishlist = Wishlist()

class ROMListView(APIView):
    def get(self, request):
        data = Roms.get_roms()
        return JsonResponse(data, safe=False)

class ROMDetailView(APIView):
    def get(self, request):
        rom_id = request.GET.get('rom_id')
        data = Roms.rom_detail(rom_id)
        return JsonResponse(data, safe=False)

class ROMSearch(APIView):
    def get(self, request):
        rom_title = request.GET.get('rom_title')
        roms = ROM.objects.filter(title__icontains=rom_title)
        serializer = ROMSerializer(roms, many=True)
        return Response(serializer.data)

class ROMCreate(APIView):
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') == False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ROMSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ROMUpdate(APIView):
    def put(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') == False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        rom_id = request.data.get('rom_id')
        rom = ROM.objects.get(id=rom_id)
        serializer = ROMSerializer(rom, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ROMDelete(APIView):
    def delete(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') == False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            rom_id = request.data.get('rom_id')
            ROM.objects.filter(id=rom_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ROM.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ROMDownload(APIView):
    def get(self, request, empresa, emulador_name, game_name):
        empresa = empresa.lower()
        emulador_name = emulador_name.lower()

        emulador = Emulador.objects.get(nome=emulador_name, empresa=empresa)
        obj = ROM.objects.get(emulador_id=emulador.id, title=game_name)
        file_path = obj.file.path
        
        if file_path:
                response = Roms.download(file_path)
                obj.qtd_download += 1
                obj.save()
                return response
        else:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

class MostPlayed(APIView):
    def get(self, request):
        data = Roms.most_played()
        return JsonResponse(data, safe=False)

#Views User
class UserListView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload['admin']:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)

class UserDetailView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        if user_id:
            user = self.get_object(user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)

class UserRegister(APIView):            
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdate(APIView):
    def put(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDelete(APIView):
    def delete(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'ID do usuário não fornecido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class UserViewWishlist(APIView):
    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload['user_id']
        user = User.objects.get(id=user_id)
        wishlist = user.wishlist.all()
        serializer = ROMSerializer(wishlist, many=True)
        return Response(serializer.data)

class UserAddWishlist(APIView):
    def post(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        rom_id = request.data.get('rom_id')
        response = Wishlist.add_to_wishlist(rom_id, token)
        return response

class UserRemoveWishlist(APIView):
    def delete(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        rom_id = request.data.get('rom_id')
        response = Wishlist.remove_wishlist(rom_id, token)
        return response

#autenticacao
class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        response = Auth.login(email, password)
        return response      

class RefreshToken(APIView):
    def get(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        response = Auth.refresh_token(refresh_token)
        return response

class ForgotPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        response = Auth.send_ForgotPassword_email(email)
        return response

class ResetPassword(APIView):
    def post(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        password = request.data.get('password')
        response = Auth.reset_password(token, password)
        return response

class ProtectedRoute(APIView):
    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        response = Auth.protected_route(token)
        return response


#emuladores e categorias
class Emuladores(APIView):
    def get(self, request):
        emuladores = Emulador.objects.all()
        serializer = EmuladorSerializer(emuladores, many=True)
        return Response(serializer.data)

class EmuladorCreate(APIView):
    def post(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        # if payload.get('admin') == False:
        #     return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EmuladorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmuladorUpdate(APIView):
    def put(self, request):
        #token = request.headers.get('Authorization', '').split(' ')[1]
        #payload = Token.decode_token(token)
        #if payload is None:
        #    return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        #if payload.get('admin') == False:
        #    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        emulador_id = request.data.get('emulador_id')
        emulador = Emulador.objects.get(id=emulador_id)
        serializer = EmuladorSerializer(emulador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmuladorDelete(APIView):
    def delete(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        # if payload.get('admin') == False:
        #     return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        emulador_id = request.data.get('emulador_id')
        try:
            emulador = Emulador.objects.get(id=emulador_id)
            emulador.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Emulador.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class EmuladorDownload(APIView):
    def get(self, request, emulador_name):
        emulador_name = emulador_name.lower()
        emulador = Emulador.objects.get(nome=emulador_name)
        file_path = emulador.file.path
        if file_path:
            response = Roms.download(file_path)
            return response
        else:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

class Categorias(APIView):
    def get(self, request):
        categorias = Categoria_Jogo.objects.all()
        serializer = CategoriaJogoSerializer(categorias, many=True)
        return Response(serializer.data)