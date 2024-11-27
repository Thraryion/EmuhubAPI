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

from ..models import Topico, Roms, Categoria_Jogo, Categoria_Forum
from ..serializer import TopicoSerializer, ROMSerializer
from ..Classes.token import Token

logger = logging.getLogger(__name__)
Token = Token()

class SearchGlobal(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Termo de pesquisa", type=openapi.TYPE_STRING)
        ],
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
        search = request.GET.get('search')
        if not search:
            return Response({"detail": "Nenhum termo de busca fornecido."}, status=400)
        
        try:
            roms = Roms.objects.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(categoria__nome__icontains=search)
            ).distinct()
            topicos = Topico.objects.filter(
                Q(titulo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(id_categoria__nome__icontains=search)
            ).distinct()
            serializer_roms = ROMSerializer(roms, many=True)
            serializer_topicos = TopicoSerializer(topicos, many=True)

            Return Response({
                'roms': serializer_roms.data,
                'topicos': serializer_topicos.data
            })

        except Exception as e:
            logger.error(f"Erro ao buscar dados: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)