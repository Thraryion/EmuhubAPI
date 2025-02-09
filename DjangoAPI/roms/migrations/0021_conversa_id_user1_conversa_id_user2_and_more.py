# Generated by Django 4.2.15 on 2024-11-25 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0020_user_is_banned_alter_denuncia_content_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversa",
            name="id_user1",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user1",
                to="roms.user",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="conversa",
            name="id_user2",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user2",
                to="roms.user",
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="ParticipantesCoversa",
        ),
    ]
