from ..models import ROM, Categoria_Jogo, Emulador
from django.core.files.storage import default_storage
from django.http import JsonResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from ..serializer import ROMSerializer
import os
import base64
import asyncio
from django.http import HttpResponse
from django.http import HttpResponse

class Roms():
    def __init__(self):
        pass

    def encode_image_to_base64(self, image):
        try:
            with image.open('rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            return None

    def get_roms(self):
        roms = ROM.objects.all()
        data = []
        for rom in roms:
            categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
            emulador = Emulador.objects.get(id=rom.emulador_id)
            jogo = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, self.encode_image_to_base64(rom.image), rom.file, emulador.empresa)
            data.append(jogo)
        return data

    def rom_detail(self, id_rom):
        try:
            rom = ROM.objects.get(id=id_rom)
            categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
            emulador = Emulador.objects.get(id=rom.emulador_id)
            data = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, self.encode_image_to_base64(rom.image), rom.file, emulador.empresa)
            return data
        except ROM.DoesNotExist:
            raise NotFound()
       

    def most_played(self):
        roms = ROM.objects.order_by('-qtd_download')[:4]
        data = []

        try:
            for rom in roms:
                categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
                emulador = Emulador.objects.get(id=rom.emulador_id)
                jogo = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, self.encode_image_to_base64(rom.image), rom.file, emulador.empresa)
                data.append(jogo)
            return data
        except ROM.DoesNotExist:
            raise NotFound()
    
    def create_data(self, id_rom, title, description, emulador, categoria, image_base64, file, empresa):
        if file is not None and hasattr(file, 'path'):
            file_name = os.path.basename(file.path)
        elif file is None:
            file_name = 'Nenhum arquivo disponível'

    rom = {
        'id': id_rom,
        'title': title,
        'description': description,
        'emulador': emulador,
        'categoria': categoria,
        'empresa': empresa,
        'image_base64': image_base64,
        'file': file_name,
    }
    return rom


    def download(file_path):
            try:
                response = FileResponse(open(file_path, 'rb'), as_attachment=True)
                return response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
