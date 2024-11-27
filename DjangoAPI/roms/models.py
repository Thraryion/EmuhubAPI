from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=125, unique = True)
    email = models.EmailField()
    password = models.CharField(max_length=128)  
    admin = models.BooleanField(default=False)
    imagem_perfil = models.ImageField(upload_to='img-perfil/')
    wishlist = models.ManyToManyField('ROM', related_name='wishlist', blank=True)
    is_active = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    notify_comments = models.BooleanField(default=True)
    notify_likes = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)

#Jogos e Emulador
class Emulador(models.Model):
    nome = models.CharField(max_length=125)
    console = models.CharField(max_length=125)
    empresa = models.CharField(max_length=40)
    emu_file = models.FileField(upload_to='emuladores/', blank=True, null=True)

class Categoria_Jogo(models.Model):
    nome = models.CharField(max_length=125)

class ROM(models.Model):
    title = models.CharField(max_length=125)
    description = models.TextField()
    categoria = models.ForeignKey('Categoria_Jogo', on_delete=models.CASCADE)
    emulador = models.ForeignKey('Emulador', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='img/' , blank=True, null=True)
    file = models.FileField(upload_to='roms/', blank=True, null=True)
    qtd_download = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#mensagens privadas
class Conversa(models.Model):
    id_user1 = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user1')
    id_user2 = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Mensagem(models.Model):
    id_conversa = models.ForeignKey('Conversa', on_delete=models.CASCADE)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    mensagem = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

#forum
class Topico(models.Model):
    titulo = models.CharField(max_length=125)
    descricao = models.TextField()
    img_topico = models.ImageField(upload_to='img-topico/', blank=True, null=True)
    id_categoria = models.ForeignKey('CategoriaForum', on_delete=models.CASCADE)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    tags = models.CharField(max_length=125, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CategoriaForum(models.Model):
    nome = models.CharField(max_length=125)

class LikeTopico(models.Model):
    id_topico = models.ForeignKey('Topico', on_delete=models.CASCADE)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('id_topico', 'id_user')

class LikeComentario(models.Model):
    id_comentario = models.ForeignKey('Comentario', on_delete=models.CASCADE)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('id_comentario', 'id_user')

class Comentario(models.Model):
    descricao = models.TextField()
    id_topico = models.ForeignKey('Topico', on_delete=models.CASCADE)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id_parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_helpful = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

class Notificacao(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    referencia_id = models.IntegerField()
    mensagem = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Denuncia(models.Model):
    reported_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reports')
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'content_id')    
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pendente')
    reviewed_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    resolution = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Moderacao(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    reason = models.TextField()
    actioned_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='moderated_actions')
    actioned_at = models.DateTimeField(auto_now_add=True)
