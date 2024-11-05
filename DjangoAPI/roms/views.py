from django.shortcuts import render
from rest_framework import generics
from django.http import HttpResponse, FileResponse, Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework.pagination import PageNumberPagination
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
from .models import ROM, User, Emulador, Categoria_Jogo, Topico, CategoriaForum, Comentario, LikeComentario, LikeTopico
from .serializer import ROMSerializer, UserSerializer, EmuladorSerializer, CategoriaJogoSerializer, TopicoDetailSerializer, ComentarioSerializer, LikeTopicoSerializer, LikeComentarioSerializer, TopicoSerializer

import base64
import logging

from django.core.files.storage import default_storage
from django.http import JsonResponse, Http404
from rest_framework import status, generics
from rest_framework.response import Response
from adrf.views import APIView
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ROM
from .Classes.token import Token

logger = logging.getLogger(__name__)

Auth = Auth()
Token = Token()
Roms = Roms()
Wishlist = Wishlist()

class ROMListView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Lista de ROMs", schema=ROMSerializer(many=True)),
            401: "Token inválido"
        })
    def get(self, request):
        data = Roms.get_roms()
        return JsonResponse(data, safe=False)

class ROMDetailView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('rom_id', openapi.IN_QUERY, description="ID do ROM", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(description="Detalhes do ROM", schema=ROMSerializer),
            404: "ROM não encontrado"
        })
    def get(self, request):
        rom_id = request.GET.get('rom_id')
        data = Roms.rom_detail(rom_id)
        return JsonResponse(data, safe=False)

class ROMSearch(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('rom_title', openapi.IN_QUERY, description="Título do ROM", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="Resultados da busca", schema=ROMSerializer(many=True)),
            404: "ROM não encontrado"
        })
    def get(self, request):
        rom_title = request.GET.get('rom_title')
        roms = ROM.objects.filter(title__icontains=rom_title)
        serializer = ROMSerializer(roms, many=True)
        return Response(serializer.data)

class ROMCreate(APIView):
    @swagger_auto_schema(
        request_body=ROMSerializer,
        responses={
            201: openapi.Response(description="ROM criado com sucesso", schema=ROMSerializer),
            400: "Dados inválidos",
            401: "Não autorizado"
        })
    def post(self, request):
        serializer = ROMSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ROMUpdate(APIView):
    @swagger_auto_schema(
        request_body=ROMSerializer,
        responses={
            200: openapi.Response(description="ROM atualizado com sucesso", schema=ROMSerializer),
            400: "Dados inválidos",
            401: "Não autorizado"
        })
    def put(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        rom_id = request.data.get('rom_id')
        try:
            rom = ROM.objects.get(id=rom_id)
        except ROM.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = ROMSerializer(rom, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ROMDelete(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('rom_id', openapi.IN_QUERY, description="ID do ROM", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: "ROM deletado com sucesso",
            400: "Dados inválidos",
            404: "ROM não encontrado"
        })
    def delete(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        rom_id = request.GET.get('rom_id')  # Corrigido para usar GET em vez de data
        try:
            ROM.objects.get(id=rom_id).delete()  # Use get() para gerar a exceção corretamente
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ROM.DoesNotExist:
            return Response({'error': 'ROM não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class ROMDownload(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('empresa', openapi.IN_QUERY, description="Empresa", type=openapi.TYPE_STRING),
            openapi.Parameter('emulador_name', openapi.IN_QUERY, description="Nome do emulador", type=openapi.TYPE_STRING),
            openapi.Parameter('game_name', openapi.IN_QUERY, description="Nome do jogo", type=openapi.TYPE_STRING)
        ],
        responses={
            200: "Download do ROM",
            404: "ROM não encontrado"
        })
    def get(self, request, empresa, emulador_name, game_name):
        empresa = empresa.lower()
        emulador_name = emulador_name.lower()

        try:
            emulador = Emulador.objects.get(nome__iexact=emulador_name, empresa__iexact=empresa)
            obj = ROM.objects.get(emulador_id=emulador.id, title=game_name)
            file_path = obj.file.path
            
            if file_path:
                response = Roms.download(file_path)
                obj.qtd_download += 1
                obj.save()
                return response
            else:
                return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        except Emulador.DoesNotExist:
            return Response({'error': 'Emulador não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ROM.DoesNotExist:
            return Response({'error': 'ROM não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class MostPlayed(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="ROMs mais jogados", schema=ROMSerializer(many=True)),
            404: "ROM não encontrado"
        })
    def get(self, request):
        data = Roms.most_played()
        return JsonResponse(data, safe=False)

#Views User
class UserListView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Lista de usuários", UserSerializer(many=True)),  
            403: "Acesso negado"
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if payload.get('admin', False):
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)

class UserDetailView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Detalhes do usuário", UserSerializer),  
            404: "Usuário não encontrado",
            401: "Token inválido"
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'ID do usuário não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegister(APIView):    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Response("Usuário criado com sucesso", UserSerializer),
            400: "Dados inválidos"
        })        
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdate(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: openapi.Response("Usuário atualizado com sucesso", UserSerializer),
            400: "Dados inválidos",
            404: "Usuário não encontrado",
            401: "Token inválido"
        })
    def put(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'ID do usuário não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class UserDelete(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID do usuário", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: "Usuário deletado com sucesso",
            400: "Dados inválidos",
            404: "Usuário não encontrado",
            401: "Token inválido"
        })
    def delete(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        
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
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Lista de desejos do usuário", ROMSerializer(many=True)),  
            401: "Token inválido"
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload['user_id']
        try:
            user = User.objects.get(id=user_id)
            wishlist = user.wishlist.all()
            serializer = ROMSerializer(wishlist, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class UserAddWishlist(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rom_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do ROM a ser adicionado", example=1)
            },
            required=['rom_id']
        ),
        responses={
            200: openapi.Response("ROM adicionado à lista de desejos com sucesso"),
            401: "Token inválido",
            400: "Dados inválidos"
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        rom_id = request.data.get('rom_id')
        if rom_id:
            response = Wishlist.add_to_wishlist(rom_id, token)
            return response
        return Response({'error': 'ID do ROM não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class UserRemoveWishlist(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rom_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do ROM a ser removido", example=1)
            },
            required=['rom_id']
        ),
        responses={
            200: openapi.Response("ROM removido da lista de desejos com sucesso"),
            401: "Token inválido",
            400: "Dados inválidos"
        })
    def delete(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        rom_id = request.data.get('rom_id')
        if rom_id:
            response = Wishlist.remove_wishlist(rom_id, token)
            return response
        return Response({'error': 'ID do ROM não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Email do usuário",
                    example="user@example.com"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Senha do usuário",
                    example="s3nh4S3gura!"
                )
            },
            required=['email', 'password']
        ),
        responses={
            200: openapi.Response("Login realizado com sucesso"),
            401: "Credenciais inválidas"
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        response = Auth.login(email, password)
        return response
   

class RefreshToken(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="O token de atualização foi renovado com sucesso."
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def get(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        response = Auth.refresh_token(refresh_token)
        return response


class ForgotPassword(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email do usuário", example="user@example.com")
            },
            required=['email']
        ),
        responses={
            200: openapi.Response( description="Um email foi enviado com instruções para redefinir a senha."),
            400: openapi.Response( description="Não foi possível encontrar um usuário com o email fornecido.")
        })
    def post(self, request):
        email = request.data.get('email')
        response = Auth.send_ForgotPassword_email(email)
        return response


class ResetPassword(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Nova senha do usuário", example="novaSenhaSegura!")
            },
            required=['password']
        ),
        responses={
            200: openapi.Response( description="A senha foi redefinida com sucesso."),
            401: openapi.Response(description="O token fornecido é inválido ou expirou.")
        })
    def post(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        password = request.data.get('password')
        response = Auth.reset_password(token, password)
        return response


class ProtectedRoute(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response( description="Acesso concedido à rota protegida."),
            401: openapi.Response( description="O token fornecido é inválido ou expirou.")
        })
    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        response = Auth.protected_route(token)
        return response


# Emuladores e Categorias
class Emuladores(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response( schema=EmuladorSerializer(many=True), description="Retorna uma lista de todos os emuladores disponíveis."),
            401: openapi.Response(description="O token fornecido é inválido ou expirou.")
        })
    def get(self, request):
        emuladores = Emulador.objects.all()
        serializer = EmuladorSerializer(emuladores, many=True)
        return Response(serializer.data)


class EmuladorCreate(APIView):
    @swagger_auto_schema(
        request_body=EmuladorSerializer,
        responses={
            201: openapi.Response( schema=EmuladorSerializer, description="O emulador foi criado com sucesso."),
            400: openapi.Response( description="Os dados fornecidos para criação do emulador são inválidos.")
        })
    def post(self, request):
        serializer = EmuladorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmuladorUpdate(APIView):
    @swagger_auto_schema(
        request_body=EmuladorSerializer,
        responses={
            200: openapi.Response( schema=EmuladorSerializer, description="O emulador foi atualizado com sucesso."),
            400: openapi.Response( description="Os dados fornecidos para atualização do emulador são inválidos."),
            404: openapi.Response( description="O emulador com o ID fornecido não foi encontrado.")
        })
    def put(self, request):
        emulador_id = request.data.get('emulador_id')
        emulador = get_object_or_404(Emulador, id=emulador_id)
        serializer = EmuladorSerializer(emulador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmuladorDelete(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('emulador_id', openapi.IN_QUERY, description="ID do emulador", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: openapi.Response(
                description="Emulador deletado com sucesso."
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Emulador não encontrado."
            )
        })
    def delete(self, request):
        emulador_id = request.data.get('emulador_id')
        try:
            emulador = Emulador.objects.get(id=emulador_id)
            emulador.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Emulador.DoesNotExist:
            return Response({'error': 'Emulador não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class EmuladorDownload(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('emulador_name', openapi.IN_QUERY, description="Nome do emulador", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Arquivo baixado com sucesso."
            ),
            404: openapi.Response(
                description="Emulador não encontrado."
            )
        })
    def get(self, request, emulador_name):
        emulador_name = emulador_name.lower()
        try:
            emulador = Emulador.objects.get(nome=emulador_name)
            file_path = emulador.file.path
            if file_path:
                response = Roms.download(file_path)
                return response
            else:
                return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        except Emulador.DoesNotExist:
            return Response({'error': 'Emulador não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class Categorias(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response( schema=CategoriaJogoSerializer(many=True), description="Retorna uma lista de todas as categorias disponíveis."),
            401: openapi.Response(description="O token fornecido é inválido ou expirou.")
        })
    def get(self, request):
        categorias = Categoria_Jogo.objects.all()
        serializer = CategoriaJogoSerializer(categorias, many=True)
        return Response(serializer.data)


# Views de Forum

class CreateTopico(APIView):    
    @swagger_auto_schema(
        request_body=TopicoSerializer,
        responses={
            201: openapi.Response(
                description="Tópico criado com sucesso.",
                schema=TopicoSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            )
        })
    def post(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TopicoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListTopicos(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Lista de tópicos.",
                schema=TopicoSerializer(many=True)
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def get(self, request):
        topicos = Topico.objects.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10  
        
        paginated_topicos = paginator.paginate_queryset(topicos, request)
        serializer = TopicoSerializer(paginated_topicos, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class UpdateTopico(APIView):
    @swagger_auto_schema(
        request_body=TopicoSerializer,
        responses={
            200: openapi.Response(
                description="Tópico atualizado com sucesso.",
                schema=TopicoSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Tópico não encontrado."
            )
        })
    def put(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        topico_id = request.data.get('topico_id')
        try:
            topico = Topico.objects.get(id=topico_id)
            serializer = TopicoSerializer(topico, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Topico.DoesNotExist:
            return Response({'error': 'Tópico não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class DeleteTopico(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('topico_id', openapi.IN_QUERY, description="ID do tópico", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: openapi.Response(
                description="Tópico deletado com sucesso."
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Tópico não encontrado."
            )
        })
    def delete(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        topico_id = request.data.get('topico_id')
        try:
            topico = Topico.objects.get(id=topico_id)
            topico.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Topico.DoesNotExist:
            return Response({'error': 'Tópico não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class CreateComentario(APIView):
    @swagger_auto_schema(
        request_body=ComentarioSerializer,
        responses={
            201: openapi.Response(
                description="Comentário criado com sucesso.",
                schema=ComentarioSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            )
        })
    def post(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = ComentarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListComentarios(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Lista de comentários.",
                schema=ComentarioSerializer(many=True)
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def get(self, request):
        comentarios = Comentario.objects.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10

        paginated_comentarios = paginator.paginate_queryset(comentarios, request)
        serializer = ComentarioSerializer(paginated_comentarios, many=True)

        return paginator.get_paginated_response(serializer.data)

class UpdateComentario(APIView):
    @swagger_auto_schema(
        request_body=ComentarioSerializer,
        responses={
            200: openapi.Response(
                description="Comentário atualizado com sucesso.",
                schema=ComentarioSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Comentário não encontrado."
            )
        })
    def put(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        comentario_id = request.data.get('comentario_id')
        try:
            comentario = Comentario.objects.get(id=comentario_id)
            serializer = ComentarioSerializer(comentario, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comentario.DoesNotExist:
            return Response({'error': 'Comentário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class DeleteComentario(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('comentario_id', openapi.IN_QUERY, description="ID do comentário", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: openapi.Response(
                description="Comentário deletado com sucesso."
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Comentário não encontrado."
            )
        })
    def delete(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        comentario_id = request.data.get('comentario_id')