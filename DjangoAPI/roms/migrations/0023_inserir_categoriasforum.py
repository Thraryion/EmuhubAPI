from django.db import migrations

def add_forum_categories(apps, schema_editor):
    Categoria_Forum = apps.get_model('roms', 'CategoriaForum')
    categorias_forum = [
        'Discussões Gerais',
        'Dúvidas',
        'Sugestões',
        'Eventos',
        'Notícias',
        'Feedbacks',
        'Suporte',
        'Desafios',
    ]
    for categoria in categorias_forum:
        Categoria_Forum.objects.create(nome=categoria)

class Migration(migrations.Migration):

    dependencies = [
        ('roms', '0022_alter_topico_tags'),  
    ]

    operations = [
        migrations.RunPython(add_forum_categories),
    ]
