from rest_framework import serializers
from roms.models import Comentario, LikeComentario, User
from .UserSerializer import UserSerializer
import base64

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
        return LikeComentario.objects.filter(id_comentario=obj.id, id_user=user_id).exists()

    def get_children(self, obj):
        children = obj.replies.all()
        return ComentarioSerializer(children, many=True, context=self.context).data

class LikeComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComentario
        fields = ['id', 'id_comentario', 'id_user']
                