from rest_framework import serializers
from roms.models import ROM, Categoria_Jogo, Emulador

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

class CategoriaJogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria_Jogo
        fields = ['id', 'nome']

class EmuladorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emulador
        fields = ['id', 'nome', 'console', 'empresa', 'emu_file']