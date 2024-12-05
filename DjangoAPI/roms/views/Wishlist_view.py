from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..Classes.wishlist import Wishlist
from ..Classes.token import Token
from ..models import User
from ..serializer import ROMSerializer, UserSerializer

logger = logging.getLogger(__name__)

Token = Token()
Wishlist = Wishlist()

class UserViewWishlist(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Lista de desejos do usuário", ROMSerializer(many=True)),  
            401: "Token inválido"
        })
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload['user_id']
        try:
            user = User.objects.get(id=user_id)
            wishlist = user.wishlist.all()
            serializer = ROMSerializer(wishlist, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class UserAddWishlist(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rom_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do ROM a ser adicionado", example=1)
            },
            required=['rom_id']
        ),
        responses={
            200: openapi.Response("ROM adicionado à lista de desejos com sucesso"),
            401: "Token inválido",
            400: "Dados inválidos"
        })
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        rom_id = request.data.get('rom_id')
        if rom_id:
            response = Wishlist.add_to_wishlist(rom_id, token)
            return response
        return Response({'error': 'ID do ROM não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class UserRemoveWishlist(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rom_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do ROM a ser removido", example=1)
            },
            required=['rom_id']
        ),
        responses={
            200: openapi.Response("ROM removido da lista de desejos com sucesso"),
            401: "Token inválido",
            400: "Dados inválidos"
        })
    def delete(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = Token.decode_token(token)
        if payload is None:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        rom_id = request.data.get('rom_id')
        if rom_id:
            response = Wishlist.remove_wishlist(rom_id, token)
            return response
        return Response({'error': 'ID do ROM não fornecido'}, status=status.HTTP_400_BAD_REQUEST)