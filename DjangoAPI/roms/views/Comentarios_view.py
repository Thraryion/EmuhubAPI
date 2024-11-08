from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..models import Comentario
from ..serializer import ComentarioSerializer

logger = logging.getLogger(__name__)

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
        comentario_id = request.data.get('comentario_id')
        try:
            comentario = Comentario.objects.get(id=comentario_id)
            comentario.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comentario.DoesNotExist:
            return Response({'error': 'Comentário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
