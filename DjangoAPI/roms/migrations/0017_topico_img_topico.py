# Generated by Django 4.2.15 on 2024-10-27 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0016_rename_id_categoria_rom_categoria_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="topico",
            name="img_Topico",
            field=models.ImageField(blank=True, null=True, upload_to="img-topico/"),
        ),
    ]
