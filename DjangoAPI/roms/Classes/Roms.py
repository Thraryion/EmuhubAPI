from ..models import ROM, Categoria_Jogo, Emulador, User
from django.core.files.storage import default_storage
from django.http import JsonResponse, Http404, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from ..serializer import ROMSerializer
import os
import base64
import asyncio
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
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
            jogo = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, categoria.nome ,self.encode_image_to_base64(rom.image), rom.file, emulador.empresa, emulador.console, emulador.nome)
            data.append(jogo)
        return data

    def get_wishlist(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            roms = user.wishlist.all()
            data = []
            for rom in roms:
                categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
                emulador = Emulador.objects.get(id=rom.emulador_id)
                jogo = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, categoria.nome, self.encode_image_to_base64(rom.image), rom.file, emulador.empresa, emulador.console, emulador.nome)
                data.append(jogo)
            return data
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)


    def search(self, search):
        try:
            roms = ROM.objects.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(categoria__nome__icontains=search) |
                Q(emulador__nome__icontains=search)
            ).distinct()

            data = []
            for rom in roms:
                categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
                emulador = Emulador.objects.get(id=rom.emulador_id)
                jogo = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, categoria.nome, self.encode_image_to_base64(rom.image), rom.file, emulador.empresa, emulador.console, emulador.nome)
                data.append(jogo)

            return data
        except Exception as e:
            return Response({'error': 'Erro interno do servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def rom_detail(self, id_rom):
        try:
            rom = ROM.objects.get(id=id_rom)
            categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
            emulador = Emulador.objects.get(id=rom.emulador_id)
            data = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, categoria.nome ,self.encode_image_to_base64(rom.image), rom.file, emulador.empresa, emulador.console, emulador.nome)
            return data
        except ROM.DoesNotExist:
            raise NotFound()
       

    def most_played(self):
        roms = ROM.objects.order_by('-qtd_download')[:4]
        data = []
        print(roms.file)

        try:
            for rom in roms:
                categoria = Categoria_Jogo.objects.get(id=rom.categoria_id)
                emulador = Emulador.objects.get(id=rom.emulador_id)
                jogo = self.create_data(rom.id, rom.title, rom.description, rom.emulador_id, rom.categoria_id, categoria.nome, self.encode_image_to_base64(rom.image), rom.file, emulador.empresa, emulador.console, emulador.nome)
                data.append(jogo)
            return data
        except ROM.DoesNotExist:
            raise NotFound()
    
    def create_data(self, id_rom, title, description, emulador, categoria, categoria_nome, image_base64, file, empresa, console, emulador_nome):
        file_name = None
        try:
            if file and hasattr(file, 'path'):
                file_name = os.path.basename(file.path)
            else:
                file_name = 'Nenhum arquivo disponível'
        except ValueError as e:
            print(f'Erro ao acessar o arquivo para ROM ID {id_rom}: {e}')
            file_name = 'Erro ao acessar o arquivo'

        rom = {
            'id': id_rom,
            'title': title,
            'description': description,
            'image_base64': image_base64,
            'emulador': {
                'nome': emulador_nome,
                'console': console,
                'empresa': empresa,
                'id': emulador,
            },
            'categoria':{
                'id': categoria,
                'nome': categoria_nome,
            },
            'file': file_name,
        }
        return rom

    def download(self, file_path):
            try:
                response = FileResponse(open(file_path, 'rb'), as_attachment=True)
                return response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def DownloadImage(self, image_path):
        try:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    response = HttpResponse(img_file.read(), content_type="image/png")
                    response['Content-Disposition'] = 'attachment; filename="image.png"'
                    return response
            else:
                return Response({'error': 'Imagem não encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
