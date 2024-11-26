from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..Classes.token import Token
from ..models import Topico, LikeTopico, User, CategoriaForum
from ..serializer import TopicoSerializer, LikeTopicoSerializer

logger = logging.getLogger(__name__)

Token = Token()

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
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']

        data = request.data.copy()
        data['id_user'] = user_id
        serializer = TopicoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListTopicos(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id_user', openapi.IN_QUERY, description="ID do usuário", type=openapi.TYPE_INTEGER)
        ],
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
        
        serializer = TopicoSerializer(topicos, many=True, context={'request': request})

        for topico_data in serializer.data:
            user = get_object_or_404(User, id=topico_data['id_user'])

            topico_data['username'] = user.username
            
            if user.imagem_perfil:
                topico_data['imagem_perfil'] = user.imagem_perfil
            else:
                topico_data['imagem_perfil'] = None

            likes = LikeTopico.objects.filter(id_topico=topico_data['id'])
            topico_data['likes'] = likes.count()
        
        return Response(serializer.data)


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
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
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
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        topico_id = request.data.get('topico_id')
        try:
            topico = Topico.objects.get(id=topico_id)
            topico.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Topico.DoesNotExist:
            return Response({'error': 'Tópico não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class TopicoDetail(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('topico_id', openapi.IN_QUERY, description="ID do tópico", type=openapi.TYPE_INTEGER),
            openapi.Parameter('id_user', openapi.IN_QUERY, description="ID do usuário", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="Detalhes do tópico.",
                schema=TopicoSerializer
            ),
            404: openapi.Response(
                description="Tópico não encontrado."
            )
        })
    def get(self, request, topico_id):
        try:
            topico = Topico.objects.get(id=topico_id)
            serializer = TopicoSerializer(topico, many=True, context={'request': request})

            img_perfil = User.objects.get(id=topico.id_user).img_perfil
            username = User.objects.get(id=topico.id_user).username
            likes = LikeTopico.objects.filter(topico_id=topico_id).count()
            data = serializer.data

            data['img_perfil'] = img_perfil
            data['username'] = username
            data['likes'] = likes

            return Response(data)
        except Topico.DoesNotExist:
            raise Http404("Tópico não encontrado")

class LikeTopicoView(APIView):
    @swagger_auto_schema(
        request_body=LikeTopicoSerializer,
        responses={
            201: openapi.Response(
                description="Like criado com sucesso.",
                schema=LikeTopicoSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            )
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        try:
            data = request.data.copy()
            data['id_user'] = user_id
            serializer = LikeTopicoSerializer(data=data)

            if LikeTopico.objects.filter(id_user=user_id, id_topico=data['id_topico']).exists():
                return Response({'error': 'Você já deu like nesse tópico'}, status=status.HTTP_400_BAD_REQUEST)
                
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UnlikeTopicoView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('topico_id', openapi.IN_QUERY, description="ID do tópico", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: openapi.Response(
                description="Like removido com sucesso."
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Like não encontrado."
            )
        })
    def delete(self, request):
        topico_id = request.GET.get('topico_id')
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        try:
            like = LikeTopico.objects.get(id_user=user_id, id_topico=topico_id)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LikeTopico.DoesNotExist:
            return Response({'error': 'Like não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class list_categorias(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Lista de categorias.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'categorias': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'nome': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            )
        })
    def get(self, request):
        categorias = CategoriaForum.objects.all()
        categorias_data = [{'id': categoria.id, 'categoria': categoria.nome} for categoria in categorias]
        return Response({'categorias': categorias_data})
