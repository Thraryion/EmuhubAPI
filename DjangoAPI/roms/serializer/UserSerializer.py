from rest_framework import serializers
from roms.models import User
import base64

class UserSerializer(serializers.ModelSerializer):
    img_perfil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username',  'password', 'email', 'admin', 'imagem_perfil', 'img_perfil', 'is_active', 'is_banned']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'admin': {'required': False},
            'username': {'required': False},
            'email': {'required': False},
            'imagem_perfil': {'write_only': True, 'required': False},
        }

    def get_img_perfil(self, obj):
        if obj.imagem_perfil and obj.imagem_perfil.name:
            try:
                with open(obj.imagem_perfil.path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            except Exception:
                return None
        return None

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Este nome de usuário já está em uso."})

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Este email já está em uso."})

        return data

    def create(self, validated_data):
        imagem_perfil = validated_data.pop('imagem_perfil', None)

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            admin=validated_data.get('admin', False)
        )
        user.set_password(validated_data['password'])

        if imagem_perfil:
            user.imagem_perfil = imagem_perfil

        user.save()
        return user

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data['username']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'admin' in validated_data:
            instance.admin = validated_data['admin']
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        if 'imagem_perfil' in validated_data:
            instance.imagem_perfil = validated_data['imagem_perfil']

        instance.save()
        return instance