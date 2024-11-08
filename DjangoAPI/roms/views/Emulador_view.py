from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

from ..Classes.wishlist import Wishlist
from ..Classes.Roms import Roms
from ..models import Emulador, Categoria_Jogo
from ..serializer import EmuladorSerializer, CategoriaJogoSerializer

class Emuladores(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(schema=EmuladorSerializer(many=True), description="Retorna uma lista de todos os emuladores disponíveis."),
            401: openapi.Response(description="O token fornecido é inválido ou expirou.")
        }
    )
    def get(self, request):
        emuladores = Emulador.objects.all()
        serializer = EmuladorSerializer(emuladores, many=True)
        return Response(serializer.data)


class EmuladorCreate(APIView):
    @swagger_auto_schema(
        request_body=EmuladorSerializer,
        responses={
            201: openapi.Response(schema=EmuladorSerializer, description="O emulador foi criado com sucesso."),
            400: openapi.Response(description="Os dados fornecidos para criação do emulador são inválidos.")
        }
    )
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
            200: openapi.Response(schema=EmuladorSerializer, description="O emulador foi atualizado com sucesso."),
            400: openapi.Response(description="Os dados fornecidos para atualização do emulador são inválidos."),
            404: openapi.Response(description="O emulador com o ID fornecido não foi encontrado.")
        }
    )
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
            204: openapi.Response(description="Emulador deletado com sucesso."),
            400: openapi.Response(description="Dados inválidos."),
            404: openapi.Response(description="Emulador não encontrado.")
        }
    )
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
            200: openapi.Response(description="Arquivo baixado com sucesso."),
            404: openapi.Response(description="Emulador não encontrado.")
        }
    )
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
            200: openapi.Response(schema=CategoriaJogoSerializer(many=True), description="Retorna uma lista de todas as categorias disponíveis."),
            401: openapi.Response(description="O token fornecido é inválido ou expirou.")
        }
    )
    def get(self, request):
        categorias = Categoria_Jogo.objects.all()
        serializer = CategoriaJogoSerializer(categorias, many=True)
        return Response(serializer.data)
