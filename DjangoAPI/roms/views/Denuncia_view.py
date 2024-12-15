from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
import logging

from ..Classes.wishlist import Wishlist
from ..Classes.token import Token
from ..models import Denuncia, User, Topico, Comentario
from ..serializer import DenunciaSerializer

Token = Token()
logger = logging.getLogger(__name__)

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
        data = request.data.copy()
        
        try:
            content_type_str = data.get('content_type')
            content_id = data.get('content_id')
            
            if not content_type_str or not content_id:
                return Response({'error': 'Campos content_type e content_id são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                model_class = {
                    'post': Post,
                    'comentario': Comentario
                }.get(content_type_str.lower())
                
                if not model_class:
                    return Response({'error': 'Tipo de conteúdo inválido.'}, status=status.HTTP_400_BAD_REQUEST)
                
                content_type = ContentType.objects.get_for_model(model_class)
                data['content_type'] = content_type.id

            except ContentType.DoesNotExist:
                return Response({'error': 'Tipo de conteúdo não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not model_class.objects.filter(id=content_id).exists():
                return Response({'error': 'Objeto associado ao content_id não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = DenunciaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Erro ao criar denúncia: {str(e)}")
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

class update_status(APIView):
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
