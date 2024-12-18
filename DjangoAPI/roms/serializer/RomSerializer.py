from rest_framework import serializers
from roms.models import ROM, Categoria_Jogo, Emulador
import base64

class ROMSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.SerializerMethodField()
    rom_image = serializers.SerializerMethodField()

    class Meta:
        model = ROM
        fields = ['title', 'description', 'categoria', 'categoria_nome','emulador', 'rom_image', 'image', 'file']
        extra_kwargs = {
            'image': {'required': False},
            'file': {'required': False},
            'title': {'required': False},
            'categoria': {'required': False},
            'emulador': {'required': False},
            'description': {'required': False},
            'categoria_nome': {'read_only': True},
            'rom_image': {'read_only': True}
        }

    def get_categoria_nome(self, obj):
        categoria = Categoria_Jogo.objects.get(id=obj.categoria_id)
        return categoria.nome
    
    def get_rom_image(self, obj):
        if obj.image:
            try:
                with open(obj.image.path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            except Exception:
                return None
        return None

class CategoriaJogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria_Jogo
        fields = ['id', 'nome']

class EmuladorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emulador
        fields = ['id', 'nome', 'console', 'empresa', 'emu_file']