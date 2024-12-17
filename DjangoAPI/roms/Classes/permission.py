from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException
from .token import Token

Token = Token()

class UnauthorizedException(APIException):
    status_code = 401
    default_detail = 'Token inválido ou não fornecido.'
    default_code = 'unauthorized'

class ForbiddenException(APIException):
    status_code = 403
    default_detail = 'Permissão negada.'
    default_code = 'forbidden'

class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            raise UnauthorizedException('Token não fornecido ou mal formatado.')
        
        try:
            token = auth_header.split(' ')[1]
            payload = Token.decode_token(token)
        except (IndexError, Exception):
            raise UnauthorizedException('Token inválido.')

        if not payload:
            raise UnauthorizedException('Token inválido.')

        if not payload.get('admin'):
            raise ForbiddenException('Permissão negada: apenas administradores.')

        request.payload = payload
        return True

class IsUserPermission(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            raise UnauthorizedException('Token não fornecido ou mal formatado.')
        
        try:
            token = auth_header.split(' ')[1]
            payload = Token.decode_token(token)
        except (IndexError, Exception):
            raise UnauthorizedException('Token inválido.')

        if not payload:
            raise UnauthorizedException('Token inválido.')

        if not payload.get('admin'):
            raise ForbiddenException('Permissão negada para este recurso.')

        request.payload = payload
        return True
