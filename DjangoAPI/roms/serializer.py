from rest_framework import serializers
from .models import ROM, User, Conversa, Mensagem, Topico, Emulador, Categoria_Jogo, Comentario, LikeComentario, LikeTopico, CategoriaForum, Denuncia
import base64

#rom serializer
class ROMSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.SerializerMethodField()

    class Meta:
        model = ROM
        fields = ['title', 'description', 'categoria', 'categoria_nome','emulador', 'image', 'file']
        extra_kwargs = {
            'image': {'required': False},
            'file': {'required': False},
            'title': {'required': False},
            'categoria': {'required': False},
            'emulador': {'required': False},
            'description': {'required': False},
        }

    def get_categoria_nome(self, obj):
        categoria = Categoria_Jogo.objects.get(id=obj.categoria_id)
        return categoria.nome

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
class CategoriaForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaForum
        fields = ['id', 'nome']

class TopicoSerializer(serializers.ModelSerializer):
    has_liked = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    img_topico64 = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    comentarios = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'img_topico','img_topico64', 'descricao', 'id_categoria', 'tags', 'categoria', 'id_user', 'user', 'comentarios', 'likes', 'created_at', 'updated_at', 'has_liked']
        extra_kwargs = {
            'id_categoria': {'write_only': True},
            'categoria': {'read_only': True},
            'id_user': {'write_only': True},
            'user': {'read_only': True},
            'has_liked': {'read_only': True},
            'likes': {'read_only': True},
            'comentarios': {'read_only': True},
            'img_topico': {'write_only': True},
            'img_topico64': {'read_only': True},
        }

    def get_user(self, obj):
        user = User.objects.get(id=obj.id_user.id)
        return UserSerializer(user).data
    
    def get_likes(self, obj):
        likes = LikeTopico.objects.filter(id_topico=obj.id).count()
        return likes
    
    def get_comentarios(self, obj):
        comentarios = Comentario.objects.filter(id_topico=obj.id, comentario_delete=False).count()
        return comentarios

    def get_img_topico64(self, obj):
        if obj.img_topico:
            try:
                with open(obj.img_topico.path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            except Exception:
                return None
        return None

    def get_has_liked(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return LikeTopico.objects.filter(id_topico=obj.id, id_user=user_id).exists()

    def get_categoria(self, obj):
        categoria = CategoriaForum.objects.get(id=obj.id_categoria.id)
        return CategoriaForumSerializer(categoria).data
        
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
    categoria = serializers.SerializerMethodField()
    img_topico64 = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    comentarios = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    obj_comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Topico
        fields = ['id', 'titulo', 'img_topico', 'img_topico64', 'descricao', 'tags', 'id_categoria', 'categoria', 'id_user', 'user', 'comentarios', 'obj_comentarios', 'likes', 'created_at', 'updated_at', 'has_liked']
        extra_kwargs = {
            'id_categoria': {'write_only': True},
            'categoria': {'read_only': True},
            'id_user': {'write_only': True},
            'user': {'read_only': True},
            'has_liked': {'read_only': True},
            'likes': {'read_only': True},
            'comentarios': {'read_only': True},
            'img_topico': {'write_only': True},
            'img_topico64': {'read_only': True},
        }

    def get_user(self, obj):
        user = User.objects.get(id=obj.id_user.id)
        return UserSerializer(user).data

    def get_obj_comentarios(self, obj):
        user_id = self.context.get('user_id')
        comentarios = Comentario.objects.filter(id_topico=obj.id, comentario_delete=False, id_parent__isnull=True)
        return ComentarioSerializer(comentarios, context={'user_id': user_id}, many=True).data
    
    def get_likes(self, obj):
        likes = LikeTopico.objects.filter(id_topico=obj.id).count()
        return likes
    
    def get_comentarios(self, obj):
        comentarios = Comentario.objects.filter(id_topico=obj.id, comentario_delete=False).count()
        return comentarios

    def get_img_topico64(self, obj):
        if obj.img_topico:
            try:
                with open(obj.img_topico.path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            except Exception:
                return None
        return None

    def get_has_liked(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return LikeTopico.objects.filter(id_topico=obj.id, id_user=user_id).exists()

    def get_categoria(self, obj):
        categoria = CategoriaForum.objects.get(id=obj.id_categoria.id)
        return CategoriaForumSerializer(categoria).data

class ComentarioSerializer(serializers.ModelSerializer):
    has_liked = serializers.SerializerMethodField()
    type_content = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ['id', 'id_topico', 'id_user', 'descricao', 'type_content', 'user', 'is_helpful', 'id_parent', 'created_at', 'updated_at', 'has_liked', 'children']
        extra_kwargs = {
            'type_content': {'read_only': True},
            'has_liked': {'read_only': True},
            'id_user': {'required': False},
        }

    def get_user(self, obj):
        user = User.objects.get(id=obj.id_user.id)
        return UserSerializer(user).data

    def get_type_content(self, obj):
        if obj.id_parent is None:
            return 'topico'
        else:
            return 'comentario'

    def get_has_liked(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return LikeTopico.objects.filter(id_topico=obj.id, id_user=user_id).exists()

    def get_children(self, obj):
        children = obj.replies.all()
        return ComentarioSerializer(children, many=True, context=self.context).data
                

class DenunciaSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Denuncia
        fields = [
            'id',
            'reported_by',
            'content_type',
            'content_type_name',
            'content_id',
            'reason',
            'status',
            'reviewed_by',
            'resolution',
            'created_at',
            'updated_at',
        ]

    def get_content_type_name(self, obj):
        return obj.content_type.model