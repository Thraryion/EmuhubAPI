from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..models import Mensagem, Conversa
from ..serializer import MensagemSerializer, ConversaDetailSerializer, ConversaSerializer
from ..Classes.token import Token

logger = logging.getLogger(__name__)
Token = Token()

class MensagemCreate(APIView):
    @swagger_auto_schema(
        request_body=MensagemSerializer,
        responses={
            201: openapi.Response(
                description="Mensagem criada com sucesso.",
                schema=MensagemSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data.copy()
        data['id_user'] = payload['user_id']
        serializer = MensagemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversaCreate(APIView):
    @swagger_auto_schema(
        request_body=ConversaSerializer,
        responses={
            201: openapi.Response(
                description="Conversa criada com sucesso.",
                schema=MensagemSerializer
            ),
            400: openapi.Response(
                description="Dados inválidos."
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data.copy()
        data['id_user'] = payload['user_id']
        serializer = ConversaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Detail_Conversa(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="id da conversa", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="Lista de conversas.",
                schema=ConversaDetailSerializer(many=True)
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        id = request.query_params.get('id')
        conversas = Conversa.objects.filter(id=id)
        mensagens = Mensagem.objects.filter(id_conversa=id)

        conversas['mensagens'] = mensagens
        serializer = ConversaDetailSerializer(conversas, many=True)

        return Response(serializer.data)
        
class List_Conversas(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Lista de conversas.",
                schema=ConversaSerializer(many=True)
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if not payload:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        id_user = payload['user_id']
        conversas = Conversa.objects.filter(id_user1=id_user)
        serializer = ConversaSerializer(conversas, many=True)
        return Response(serializer.data)