from django.http import JsonResponse, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.core.files.storage import default_storage
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..Classes.wishlist import Wishlist
from ..Classes.Roms import Roms
from ..Classes.Auth import Auth
from ..Classes.token import Token
from ..models import ROM, Emulador
from ..serializer import ROMSerializer

import logging

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
        try:
            data = Roms.get_roms()
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Erro ao obter lista de ROMs: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            rom_id = request.GET.get('rom_id')
            data = Roms.rom_detail(rom_id)
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do ROM: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            rom_title = request.GET.get('rom_title')
            roms = ROM.objects.filter(title__icontains=rom_title)
            serializer = ROMSerializer(roms, many=True)
            return Response(serializer.data)
        except ROM.DoesNotExist:
            raise NotFound("ROM não encontrado")

class ROMCreate(APIView):
    @swagger_auto_schema(
        request_body=ROMSerializer,
        responses={
            201: openapi.Response(description="ROM criado com sucesso", schema=ROMSerializer),
            400: "Dados inválidos",
            401: "Não autorizado"
        })
    def post(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        # if payload.get('admin') is False:
        #     return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = ROMSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro ao criar ROM: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ROMUpdate(APIView):
    @swagger_auto_schema(
        request_body=ROMSerializer,
        responses={
            200: openapi.Response(description="ROM atualizado com sucesso", schema=ROMSerializer),
            400: "Dados inválidos",
            401: "Não autorizado"
        })
    def put(self, request):
        # token = request.headers.get('Authorization', '').split(' ')[1]
        # payload = Token.decode_token(token)
        # if payload is None:
        #     return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        # if payload.get('admin') is False:
        #     return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
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
        rom_id = request.GET.get('rom_id') 
        try:
            ROM.objects.get(id=rom_id).delete()
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
                return Response({'error': 'File não encontrado'}, status=status.HTTP_404_NOT_FOUND)
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
        try:
            data = Roms.most_played()
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Erro ao obter ROMs mais jogados: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)