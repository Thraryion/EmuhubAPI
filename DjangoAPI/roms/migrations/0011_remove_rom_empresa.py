# Generated by Django 4.2.15 on 2024-10-08 03:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0010_rom_empresa"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rom",
            name="empresa",
        ),
    ]
