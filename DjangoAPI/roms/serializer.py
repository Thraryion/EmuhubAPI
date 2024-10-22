from rest_framework import serializers
from .models import ROM, User, Conversa, ParticipantesCoversa, Mensagem, Topico, Emulador, Categoria_Jogo, Comunidade, Comentario, LikeComentario, LikeTopico


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
            'password': {'write_only': True},
            'admin': {'required': False},
        }
    
    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Este nome de usuário já está em uso."})
        
        if User.objects.filter(email=data['email']).exists():
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

class EmuladorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emulador
        fields = ['id', 'nome', 'console', 'empresa']

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

class ParticipantesConversaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantesCoversa
        fields = ['id', 'id_conversa', 'id_user']

class ConversaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversa
        fields = ['id', 'created_at', 'updated_at']

class ConversaDetailSerializer(serializers.ModelSerializer):
    mensagens = MensagemSerializer(many=True, read_only=True, source='mensagem_set')

    class Meta:
        model = Conversa
        fields = ['id', 'mensagens', 'created_at', 'updated_at']

#Forum serializers
class ComunidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunidade
        fields = ['id', 'nome', 'users', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topico
        fields = ['id', 'id_topico', 'id_user']


class TopicoDetailSerializer(serializers.ModelSerializer):
    comentarios = ComentarioSerializer(many=True, read_only=True, source='comentario_set')

    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'descricao', 'id_categoria', 'id_user', 'comentarios', 'created_at', 'updated_at']

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = ['id', 'id_topico', 'id_user', 'comentario', 'created_at', 'updated_at']
