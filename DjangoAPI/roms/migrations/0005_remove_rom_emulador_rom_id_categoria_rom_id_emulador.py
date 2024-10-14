# Generated by Django 4.2.15 on 2024-09-24 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0004_emulador"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rom",
            name="emulador",
        ),
        migrations.AddField(
            model_name="rom",
            name="id_categoria",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="roms.categoria_jogo",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rom",
            name="id_emulador",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="roms.emulador",
            ),
            preserve_default=False,
        ),
    ]
