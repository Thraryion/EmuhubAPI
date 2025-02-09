# Generated by Django 4.2.15 on 2024-09-24 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("roms", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Categoria_Forum",
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
            ],
        ),
        migrations.CreateModel(
            name="Categoria_Jogo",
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
            ],
        ),
        migrations.CreateModel(
            name="Conversa",
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
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="rom",
            name="emulador",
            field=models.CharField(default=1, max_length=125),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rom",
            name="qtd_download",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="rom",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="roms/"),
        ),
        migrations.AlterField(
            model_name="rom",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="img/"),
        ),
        migrations.CreateModel(
            name="User",
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
                ("username", models.CharField(max_length=125, unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("password", models.CharField(max_length=128)),
                ("admin", models.BooleanField(default=False)),
                ("imagem_perfil", models.ImageField(upload_to="img-perfil/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "wishlist",
                    models.ManyToManyField(
                        blank=True, related_name="wishlist", to="roms.rom"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Topico",
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
                ("titulo", models.CharField(max_length=125)),
                ("descricao", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id_categoria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="roms.categoria_forum",
                    ),
                ),
                (
                    "id_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Postagem",
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
                ("titulo", models.CharField(max_length=125)),
                ("descricao", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
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
        ),
        migrations.CreateModel(
            name="ParticipantesCoversa",
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
                (
                    "id_conversa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.conversa"
                    ),
                ),
                (
                    "id_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Mensagem",
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
                ("mensagem", models.TextField()),
                ("lida", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "id_conversa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.conversa"
                    ),
                ),
                (
                    "id_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="roms.user"
                    ),
                ),
            ],
        ),
    ]
