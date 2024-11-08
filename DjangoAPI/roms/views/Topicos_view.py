from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..models import Topico
from ..serializer import TopicoSerializer

logger = logging.getLogger(__name__)

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
            openapi.Parameter('topico_id', openapi.IN_QUERY, description="ID do tópico", type=openapi.TYPE_INTEGER)
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
            serializer = TopicoSerializer(topico)
            return Response(serializer.data)
        except Topico.DoesNotExist:
            raise Http404("Tópico não encontrado")