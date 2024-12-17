from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import User
from ..serializer import UserSerializer
from ..Classes.token import Token
from ..Classes.permission import IsAdminPermission, IsUserPermission

import logging

logger = logging.getLogger(__name__)

Token = Token()

class UserListView(APIView):

    permission_classes = [IsAdminPermission]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Lista de usuários", UserSerializer(many=True)),  
            403: "Acesso negado"
        })
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):

    permission_classes = [IsUserPermission]

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Detalhes do usuário", UserSerializer),  
            404: "Usuário não encontrado",
            401: "Token inválido"
        })
    def get(self, request):
        payload = request.payload
        user_id = payload.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'ID do usuário não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegister(APIView):    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Response("Usuário criado com sucesso", UserSerializer),
            400: "Dados inválidos"
        })        

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdate(APIView):

    permission_classes = [IsUserPermission]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: openapi.Response("Usuário atualizado com sucesso", UserSerializer),
            400: "Dados inválidos",
            404: "Usuário não encontrado",
            401: "Token inválido"
        })
    def put(self, request):
        payload = request.payload
        user_id = payload.get('user_id')
        if not user_id:
            return Response({'error': 'ID do usuário não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserDelete(APIView):
    
    permission_classes = [IsUserPermission]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID do usuário", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: "Usuário deletado com sucesso",
            400: "Dados inválidos",
            404: "Usuário não encontrado",
            401: "Token inválido"
        })
    def delete(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'ID do usuário não fornecido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
