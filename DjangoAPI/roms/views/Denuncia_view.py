from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

from ..Classes.wishlist import Wishlist
from ..Classes.token import Token
from ..models import Denuncia, User
from ..serializer import DenunciaSerializer

Token = Token()

class CreateDenuncia(APIView):
    @swagger_auto_schema(
        request_body=DenunciaSerializer,
        responses={
            201: openapi.Response(description="Denúncia criada com sucesso", schema=DenunciaSerializer),
            400: "Dados inválidos",
            401: "Não autorizado"
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = DenunciaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro ao criar denúncia: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class List_Denuncia(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Lista de denúncias", schema=DenunciaSerializer(many=True)),
            401: "Não autorizado"
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            denuncias = Denuncia.objects.all()
            serializer = DenunciaSerializer(denuncias, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao listar denúncias: {e}")
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class banned_User(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID do usuário", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: "Usuário banido com sucesso",
            400: "Dados inválidos",
            401: "Não autorizado",
            404: "Usuário não encontrado"
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.GET.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.is_banned = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class uptade_status(APIView):
    @swagger_auto_schema(
        request = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(type=openapi.TYPE_STRING, description="O status da denúncia"),
                "denuncia_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID da denúncia"),
                "resolution": openapi.Schema(type=openapi.TYPE_STRING, description="Resolução da denúncia"),
            },
            required=["status", "denuncia_id"]
        ),
        responses={
            200: "Status da denúncia atualizado com sucesso",
            400: "Dados inválidos",
            401: "Não autorizado",
            404: "Denúncia não encontrada"
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        if payload.get('admin') is False:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        denuncia_id = request.data.get('denuncia_id')
        status = request.data.get('status')
        resolution = request.data.get('resolution')
        try:
            denuncia = Denuncia.objects.get(id=denuncia_id)
            denuncia.status = status
            denuncia.resolution = resolution
            denuncia.save()
            return Response(status=status.HTTP_200_OK)
        except Denuncia.DoesNotExist:
            return Response({'error': 'Denuncia not found'}, status=status.HTTP_404_NOT_FOUND)