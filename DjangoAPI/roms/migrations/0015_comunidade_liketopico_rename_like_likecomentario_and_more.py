# Generated by Django 4.2.15 on 2024-10-23 00:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0014_comentario_like"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comunidade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=125)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "users",
                    models.ManyToManyField(related_name="comunidades", to="roms.user"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LikeTopico",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "id_topico",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.topico"
                    ),
                ),
                (
                    "id_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.user"
                    ),
                ),
            ],
            options={
                "unique_together": {("id_topico", "id_user")},
            },
        ),
        migrations.RenameModel(
            old_name="Like",
            new_name="LikeComentario",
        ),
        migrations.RenameField(
            model_name="rom",
            old_name="categoria",
            new_name="id_categoria",
        ),
        migrations.RenameField(
            model_name="rom",
            old_name="emulador",
            new_name="id_emulador",
        ),
        migrations.AlterUniqueTogether(
            name="likecomentario",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="comentario",
            name="id_postagem",
        ),
        migrations.AddField(
            model_name="comentario",
            name="id_topico",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="roms.topico"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="likecomentario",
            name="id_comentario",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="roms.comentario",
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="likecomentario",
            unique_together={("id_comentario", "id_user")},
        ),
        migrations.DeleteModel(
            name="Postagem",
        ),
        migrations.RemoveField(
            model_name="likecomentario",
            name="id_postagem",
        ),
        migrations.AddField(
            model_name="topico",
            name="id_comunidade",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="roms.comunidade",
            ),
            preserve_default=False,
        ),
    ]
