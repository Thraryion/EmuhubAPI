# Generated by Django 4.2.15 on 2024-10-23 00:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0015_comunidade_liketopico_rename_like_likecomentario_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="rom",
            old_name="id_categoria",
            new_name="categoria",
        ),
        migrations.RenameField(
            model_name="rom",
            old_name="id_emulador",
            new_name="emulador",
        ),
    ]
