from rest_framework import serializers
from .models import ROM, User, Conversa, Mensagem, Topico, Emulador, Categoria_Jogo, Comentario, LikeComentario, LikeTopico, CategoriaForum, Denuncia


#rom serializer
class ROMSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.SerializerMethodField()

    class Meta:
        model = ROM
        fields = ['title', 'description', 'categoria', 'categoria_nome','emulador', 'image', 'file']

    def get_categoria_nome(self, obj):
        categoria = Categoria_Jogo.objects.get(id=obj.categoria_id)
        return categoria.nome

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'admin', 'imagem_perfil', 'is_active', 'is_banned']
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
    id_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 
    username = serializers.SerializerMethodField()

    class Meta:
        model = Mensagem
        fields = ['id', 'id_conversa', 'id_user', 'username', 'mensagem', 'created_at']

    def get_username(self, obj):
        return obj.id_user.username

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
    has_liked = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()

    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'img_topico', 'descricao', 'id_categoria', 'categoria' ,'id_user', 'tags', 'topico_delete', 'created_at', 'updated_at', 'has_liked']

    def get_has_liked(self, obj):
        id_user = self.context['request'].user.id if self.context.get('request') else None
        
        if id_user is None:
            return False
        else:
            return LikeTopico.objects.filter(id_topico=obj.id, id_user=id_user).exists()

    def get_categoria(self, obj):
        categoria = CategoriaForum.objects.get(id=obj.id_categoria.id)
        return categoria.nome 
        
class LikeTopicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeTopico
        fields = ['id', 'id_topico', 'id_user']

class LikeComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComentario
        fields = ['id', 'id_comentario', 'id_user']

class TopicoDetailSerializer(serializers.ModelSerializer):
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'img_topico', 'descricao', 'id_categoria', 'id_user', 'tags', 'created_at', 'updated_at', "has_liked"]

    def get_has_liked(self, obj):
            id_user = self.context['request'].user.id if self.context.get('request') else None
            
            if id_user is None:
                return False
            else:
                return LikeTopico.objects.filter(id_topico=obj.id, id_user=id_user).exists()

class ComentarioSerializer(serializers.ModelSerializer):
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ['id', 'id_topico', 'id_user', 'descricao', 'comentario_delete', 'created_at', 'updated_at', 'has_liked']

    def get_has_liked(self, obj):
            id_user = self.context['request'].id_user if self.context.get('request') else None
            if id_user is None:
                return False
            else:
                return LikeComentario.objects.filter(id_comentario=obj.id, id_user=id_user).exists()

class DenunciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Denuncia
        fields = ['id', 'reported_by', 'content_type', 'content_id', 'reason', 'status', 'reviewed_by', 'resolution', 'created_at', 'updated_at']
