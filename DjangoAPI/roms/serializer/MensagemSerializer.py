# from rest_framework import serializers
# from roms.models import ROM, User, Conversa, Mensagem, Topico, Emulador, Categoria_Jogo, Comentario, LikeComentario, LikeTopico, CategoriaForum, Denuncia
# import base64

# #gerencia criacao e listagem de mensagens
# class MensagemSerializer(serializers.ModelSerializer):
#     id_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 
#     username = serializers.SerializerMethodField()

#     class Meta:
#         model = Mensagem
#         fields = ['id', 'id_conversa', 'id_user', 'username', 'mensagem', 'created_at']

#     def get_username(self, obj):
#         return obj.id_user.username

# class ConversaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Conversa
#         fields = ['id','id_user1', 'id_user2', 'created_at', 'updated_at']


# class ConversaDetailSerializer(serializers.ModelSerializer):
#     mensagens = MensagemSerializer(many=True, read_only=True, source='mensagem_set')

#     class Meta:
#         model = Conversa
#         fields = ['id', 'mensagens', 'created_at', 'updated_at']
