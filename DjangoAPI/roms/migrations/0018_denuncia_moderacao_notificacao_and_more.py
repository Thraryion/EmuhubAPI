# Generated by Django 4.2.15 on 2024-10-28 00:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0017_topico_img_topico"),
    ]

    operations = [
        migrations.CreateModel(
            name="Denuncia",
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
                ("content_id", models.IntegerField()),
                ("content_type", models.CharField(max_length=50)),
                ("reason", models.TextField()),
                ("status", models.CharField(default="pendente", max_length=20)),
                ("resolution", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Moderacao",
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
                ("action", models.CharField(max_length=50)),
                ("reason", models.TextField()),
                ("actioned_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Notificacao",
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
                ("tipo", models.CharField(max_length=50)),
                ("referencia_id", models.IntegerField()),
                ("mensagem", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
            ],
        ),
        migrations.RenameModel(
            old_name="Categoria_Forum",
            new_name="CategoriaForum",
        ),
        migrations.RenameField(
            model_name="topico",
            old_name="img_Topico",
            new_name="img_topico",
        ),
        migrations.RemoveField(
            model_name="topico",
            name="id_comunidade",
        ),
        migrations.AddField(
            model_name="comentario",
            name="is_helpful",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="notify_comments",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="notify_likes",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="notify_messages",
            field=models.BooleanField(default=True),
        ),
        migrations.DeleteModel(
            name="Comunidade",
        ),
        migrations.AddField(
            model_name="notificacao",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="roms.user"
            ),
        ),
        migrations.AddField(
            model_name="moderacao",
            name="actioned_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="moderated_actions",
                to="roms.user",
            ),
        ),
        migrations.AddField(
            model_name="moderacao",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="roms.user"
            ),
        ),
        migrations.AddField(
            model_name="denuncia",
            name="reported_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reports",
                to="roms.user",
            ),
        ),
        migrations.AddField(
            model_name="denuncia",
            name="reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reviewed_reports",
                to="roms.user",
            ),
        ),
    ]
