# Generated by Django 4.2.15 on 2024-11-25 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0021_conversa_id_user1_conversa_id_user2_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topico",
            name="tags",
            field=models.ManyToManyField(blank=True, to="roms.tags"),
        ),
    ]
