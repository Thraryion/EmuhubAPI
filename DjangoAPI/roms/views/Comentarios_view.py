from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..models import Comentario, LikeComentario, User, Topico
from ..serializer import ComentarioSerializer, LikeComentarioSerializer
from ..Classes.token import Token
from ..Classes.notificacoes import PusherClient

logger = logging.getLogger(__name__)
Token = Token()
Pusher = PusherClient()

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
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload.get('user_id')
        user = get_object_or_404(User, id=user_id)

        topico_id = request.data.get('id_topico')
        if not topico_id:
            return Response({'error': 'O campo id_topico é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        id_user_comentario = None

        if data.get('id_parent'):
            comentario = get_object_or_404(Comentario, id=data['id_parent'])
            id_user_comentario = comentario.id_user
        else:
            topico = get_object_or_404(Topico, id=topico_id)
            id_user_comentario = topico.id_user

        data['id_user'] = user_id
        serializer = ComentarioSerializer(data=data)
        
        print(id_user_comentario)

        if serializer.is_valid():
            serializer.save()

            try:
                Pusher.notificarComentario(user.username, id_user_comentario ,topico_id)
            except Exception as e:
                logging.error(f"Erro ao enviar notificação de comentario: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'error': 'Dados inválidos.', 'detalhes': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
        id_topico = request.GET.get('id_topico')
        comentarios = Comentario.objects.filter(id_topico=id_topico).order_by('-created_at')
        serializer = ComentarioSerializer(comentarios, many=True)
        return Response(serializer.data)

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
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        comentario_id = request.data.get('id')
        user_id = payload['user_id']
        data = request.data.copy()
        data['id_user'] = user_id
        try:
            comentario = Comentario.objects.get(id=comentario_id)
            serializer = ComentarioSerializer(comentario, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comentario.DoesNotExist:
            return Response({'error': 'Comentário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class DeleteComentario(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do comentário")
            }
        ),
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
        comentario_id = request.data.get('id')
        try:
            comentario = Comentario.objects.get(id=comentario_id)
            comentario.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comentario.DoesNotExist:
            return Response({'error': 'Comentário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class LikeComentarioView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_comentario': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do comentário")
            }
        ),
        responses={
            200: openapi.Response(
                description="Like adicionado com sucesso.",
                schema=ComentarioSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Comentário não encontrado."
            )
        })
    def post(self, request):
        comentario_id = request.data.get('id_comentario')
        comentario = Comentario.objects.get(id=comentario_id)

        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        user = User.objects.get(id=user_id)

        data = request.data.copy()
        data['id_user'] = user_id
        try:
            serializer = LikeComentarioSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                Pusher.notificarLike(user.username, 'Comentario', comentario.id_user_id ,comentario_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UnlikeComentarioView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do comentário")
            }
        ),
        responses={
            200: openapi.Response(
                description="Like removido com sucesso.",
                schema=ComentarioSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Comentário não encontrado."
            )
        })
    def delete(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = payload['user_id']
        comentario_id = request.data.get('id')
        try:
            like = LikeComentario.objects.get(id_user=user_id, id_comentario=comentario_id)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LikeComentario.DoesNotExist:
            return Response({'error': 'Like não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class ComentarioIsHelpful(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID do comentário", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="Comentário é útil.",
                schema=ComentarioSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            404: openapi.Response(
                description="Comentário não encontrado."
            )
        })
    def post(self, request):
        comentario_id = request.data.get('id')
        try:
            comentario = Comentario.objects.get(id=comentario_id)
            comentario.is_helpful = True
            comentario.save()
            serializer = ComentarioSerializer(comentario)
            return Response(serializer.data)
        except Comentario.DoesNotExist:
            return Response({'error': 'Comentário não encontrado'}, status=status.HTTP_404_NOT_FOUND)


            