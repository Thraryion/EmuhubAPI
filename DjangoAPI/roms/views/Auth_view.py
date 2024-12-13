from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from ..Classes.Auth import Auth
from ..Classes.token import Token
from ..models import User
from ..serializer import ROMSerializer

logger = logging.getLogger(__name__)

Auth = Auth()
Token = Token()

class Login(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Email do usuário",
                    example="user@example.com"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Senha do usuário",
                    example="s3nh4S3gura!"
                )
            },
            required=['email', 'password']
        ),
        responses={
            200: openapi.Response("Login realizado com sucesso"),
            401: "Credenciais inválidas"
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        response = Auth.login(email, password)
        return response
   

class RefreshToken(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="O token de atualização foi renovado com sucesso."
            ),
            401: openapi.Response(
                description="Token inválido."
            )
        })
    def get(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        response = Auth.refresh_token(refresh_token)
        return response


class ForgotPassword(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email do usuário", example="user@example.com")
            },
            required=['email']
        ),
        responses={
            200: openapi.Response( description="Um email foi enviado com instruções para redefinir a senha."),
            400: openapi.Response( description="Não foi possível encontrar um usuário com o email fornecido.")
        })
    def post(self, request):
        email = request.data.get('email')
        response = Auth.send_ForgotPassword_email(email)
        return response


class ResetPassword(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Nova senha do usuário", example="novaSenhaSegura!")
            },
            required=['password']
        ),
        responses={
            200: openapi.Response( description="A senha foi redefinida com sucesso."),
            401: openapi.Response(description="O token fornecido é inválido ou expirou.")
        })
    def post(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        password = request.data.get('password')
        response = Auth.reset_password(token, password)
        return response

        
