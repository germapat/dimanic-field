# Generated by Django 2.1.4 on 2019-03-14 20:19

import colorfield.fields
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
from app.defs import initial_data

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('deleted', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha eliminación')),
                ('model', models.CharField(max_length=200, null=True, unique=True, verbose_name='Modelo')),
                ('label', models.CharField(max_length=200, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('icon', models.CharField(blank=True, default='list', max_length=200, null=True, verbose_name='Icono')),
                ('color', colorfield.fields.ColorField(blank=True, default='#001a7b', max_length=18, null=True, verbose_name='Color')),
                ('access', models.CharField(choices=[('public', 'Público'), ('private', 'Privado')], default='private', max_length=10, verbose_name='Tipo de acceso')),
                ('scaling', models.BooleanField(default=False, verbose_name='Escalamiento')),
                ('fields', django.contrib.postgres.fields.jsonb.JSONField(default=list, verbose_name='Campos')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='form_form_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='form_form_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Actualizado por')),
            ],
            options={
                'verbose_name': 'Formulario',
                'verbose_name_plural': 'Formularios',
                'permissions': (('add_form', 'Crear Formularios'), ('change_form', 'Actualizar Formularios'), ('view_form', 'Ver Formularios'), ('delete_form', 'Eliminar Formularios')),
                'default_permissions': (),
            },
        ),
        migrations.RunPython(initial_data)
    ]
