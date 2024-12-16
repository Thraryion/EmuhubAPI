from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from django.db.models import Q

from ..models import Topico, ROM, Categoria_Jogo, CategoriaForum
from ..serializer import TopicoSerializer, ROMSerializer
from ..Classes.token import Token
from ..Classes.Roms import Roms

logger = logging.getLogger(__name__)
Token = Token()

class SearchTopico(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'search', 
                openapi.IN_QUERY, 
                description="Termo de pesquisa", 
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Resultados da pesquisa.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'topicos': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'titulo': openapi.Schema(type=openapi.TYPE_STRING),
                                    'descricao': openapi.Schema(type=openapi.TYPE_STRING),
                                    'id_categoria': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tags': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Nenhum termo de busca fornecido."
            ),
            500: openapi.Response(
                description="Erro interno do servidor."
            )
        }
    )
    def get(self, request):
        search = request.GET.get('search')
        if not search:
            return Response({"detail": "Nenhum termo de busca fornecido."}, status=400)
        
        try:
            topicos = Topico.objects.filter(
                Q(titulo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(id_categoria__nome__icontains=search) |
                Q(tags__icontains=search),
                topico_delete=False
            ).distinct()
            serializer_topicos = TopicoSerializer(topicos, many=True)

            return Response({
                'topicos': serializer_topicos.data
            })

        except Exception as e:
            logger.error(f"Erro ao buscar dados: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchRom(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Termo de pesquisa",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Resultados da pesquisa.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'roms': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'categoria': openapi.Schema(type=openapi.TYPE_STRING),
                                    'emulador': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Nenhum termo de busca fornecido."
            ),
            500: openapi.Response(
                description="Erro interno do servidor."
            )
        }
    )
    def get(self, request):
        search = request.GET.get('search')
        if not search:
            return Response({"detail": "Nenhum termo de busca fornecido."}, status=400)
        roms = Roms()
        data = roms.search(search)

        return Response(data)