import jwt
from rest_framework import status
from rest_framework.response import Response
from ..models import User, ROM
from ..serializer import UserSerializer
from ..Classes.token import Token

Token = Token()

class Wishlist():
    def __init__(self):
        pass

    def add_to_wishlist(self, rom_id, user_id):

        user = User.objects.get(id=user_id)
        rom = ROM.objects.get(id=rom_id)

        user.wishlist.add(rom)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def remove_wishlist(self, rom_id, user_id):

        user = User.objects.get(id=user_id)
        rom = ROM.objects.get(id=rom_id)
        user.wishlist.remove(rom)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)