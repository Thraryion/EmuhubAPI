from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..Classes.wishlist import Wishlist
from ..Classes.token import Token
from ..Classes.Roms import Roms
from ..Classes.permission import IsUserPermission
from ..models import User
from ..serializer import ROMSerializer, UserSerializer

logger = logging.getLogger(__name__)

Roms = Roms()
Wishlist = Wishlist()

class UserViewWishlist(APIView):

    permission_classes = [IsUserPermission]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Lista de desejos do usuário", ROMSerializer(many=True)),  
            401: "Token inválido"
        })
    def get(self, request):
        payload = request.payload
        user_id = payload['user_id']
        wishlist = Roms.get_wishlist(user_id)
        return Response(wishlist)
        

class UserAddWishlist(APIView):

    permission_classes = [IsUserPermission]

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
        payload = request.payload
        user_id = payload['user_id']
        rom_id = request.data.get('rom_id')
        if rom_id:
            response = Wishlist.add_to_wishlist(rom_id, user_id)
            return response
        return Response({'error': 'ID do ROM não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class UserRemoveWishlist(APIView):

    permission_classes = [IsUserPermission]

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
        payload = request.payload
        user_id = payload['user_id']
        rom_id = request.data.get('rom_id')
        if rom_id:
            response = Wishlist.remove_wishlist(rom_id, user_id)
            return response
        return Response({'error': 'ID do ROM não fornecido'}, status=status.HTTP_400_BAD_REQUEST)