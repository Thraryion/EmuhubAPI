from rest_framework import serializers
from roms.models import User, Topico, Comentario, LikeTopico, CategoriaForum
from .UserSerializer import UserSerializer
from .ComentarioSerializer import ComentarioSerializer
import base64

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
