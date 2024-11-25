from rest_framework import serializers
from .models import ROM, User, Conversa, Mensagem, Topico, Emulador, Categoria_Jogo, Comentario, LikeComentario, LikeTopico, CategoriaForum


#rom serializer
class ROMSerializer(serializers.ModelSerializer):

    class Meta:
        model = ROM
        fields = ['title', 'description', 'categoria', 'emulador', 'image', 'file']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'admin']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'admin': {'required': False},
            'username': {'required': False},
            'email': {'required': False},
        }

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Este nome de usuário já está em uso."})

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Este email já está em uso."})

        return data

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            admin=validated_data.get('admin', False)
        )
        user.set_password(validated_data['password'])
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

        instance.save()
        return instance


class EmuladorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emulador
        fields = ['id', 'nome', 'console', 'empresa', 'emu_file']

class CategoriaJogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria_Jogo
        fields = ['id', 'nome']

#gerencia criacao e listagem de mensagens
class MensagemSerializer(serializers.ModelSerializer):
    id_user = serializers.ReadOnlyField(source='id_user.username')

    class Meta:
        model = Mensagem
        fields = ['id', 'id_conversa', 'id_user', 'mensagem', 'lida', 'created_at']

class ConversaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversa
        fields = ['id','id_user1', 'id_user2', 'created_at', 'updated_at']

class ConversaDetailSerializer(serializers.ModelSerializer):
    mensagens = MensagemSerializer(many=True, read_only=True, source='mensagem_set')

    class Meta:
        model = Conversa
        fields = ['id', 'mensagens', 'created_at', 'updated_at']

#Forum serializers
class TopicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'img_topico', 'descricao', 'id_categoria', 'id_user', 'tags', 'created_at', 'updated_at']
        
class LikeTopicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeTopico
        fields = ['id', 'id_topico', 'id_user']

class LikeComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComentario
        fields = ['id', 'id_comentario', 'id_user']

class TopicoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'img_topico', 'descricao', 'id_categoria', 'id_user', 'tags', 'created_at', 'updated_at']

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = ['id', 'id_topico', 'id_user', 'descricao', 'created_at', 'updated_at']
