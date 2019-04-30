from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db.utils import ProgrammingError, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from fw.rest.serializers import BaseModelSerializer
from .sysmodels import GenerateModel
from .models import *
import unicodedata

User = get_user_model()

class DataSerializer(serializers.ModelSerializer):
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('context') and kwargs['context'].get('model'):
            self.Meta.model = kwargs['context']['model']
            self.id = kwargs['context']['id']
        return super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super(DataSerializer, self).to_representation(instance)
        representation['formLabel'] = instance.form.label
        representation['formScaling'] = instance.form.scaling
        representation['created_by'] = instance.created_by.username
        representation['created_at'] = instance.updated_at.strftime("%d/%m/%Y %H:%M")
        representation['updated_by'] = instance.updated_by.username
        representation['updated_at'] = instance.updated_at.strftime("%d/%m/%Y %H:%M")
        return representation
    
    def validate_values(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Se esperaba un objecto JSON')
        elif value == {}:
            raise serializers.ValidationError('El objecto no puede estar vacío')

        return value

    def create(self, validated_data):
        validated_data['form_id'] = self.id
        instance = self.Meta.model.objects.create(**validated_data)
        instance.save()
        return instance

    class Meta:
        model = None
        fields = '__all__'
        extra_kwargs = {
            'created_by': { 'read_only': True },
            'created_at': { 'read_only': True },
            'updated_by': { 'read_only': True },
            'updated_at': { 'read_only': True },
            'deleted': { 'read_only': True },
            'form': { 'read_only': True }
        }

class FormSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(FormSerializer, self).to_representation(instance)
        representation['created_at'] = instance.updated_at.strftime("%d/%m/%Y %H:%M")
        representation['updated_at'] = instance.updated_at.strftime("%d/%m/%Y %H:%M")
        return representation

    def validate_fields(self, data):
        if isinstance(data, list):
            if len(data) == 0:
                raise serializers.ValidationError('No hay ningún campo en el formulario')
            else:
                valueslist = []
                for i in data:
                    if not isinstance(i, dict):
                        raise serializers.ValidationError('Se esperaba un objecto JSON')
                    elif i == {}:
                        raise serializers.ValidationError('El objecto no puede estar vacío')

                    if not {'name', 'label'} <= set(i):
                        raise serializers.ValidationError('Cada campo debe de tener un name y un label')

                    valueslist.append(i['name'])
                    if valueslist.count(i['name']) > 1:
                        raise serializers.ValidationError('Nombre de campo ´{}´ duplicado'.format(i['name']))

                return data
        else:
            raise serializers.ValidationError('Se esperaba un Array')

    def validate(self, data):
        data['model'] = data['label'].lower()
        data['model'] = ''.join((c for c in unicodedata.normalize('NFD', data['model']) if unicodedata.category(c) != 'Mn'))
        data['model'] = data['model'].replace(' ', '_')
        return data


    def create(self, validated_data):
        try:
            form = Form.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError({ 'label': 'Ya existe un formulario con este nombre' })
        
        dynamic_model = GenerateModel(str(validated_data['model']))
        NewModel = dynamic_model.create_model()
        Model = dynamic_model.model()

        content_type = ContentType.objects.get_for_model(Model)
        Permission.objects.bulk_create(
            [
                Permission(name='Crear registros en ' + validated_data['label'], content_type=content_type, codename='add_custom_' + validated_data['model']),
                Permission(name='Actualizar registros en ' + validated_data['label'], content_type=content_type, codename='change_custom_' + validated_data['model']),
                Permission(name='Ver registros en ' + validated_data['label'], content_type=content_type, codename='view_custom_' + validated_data['model']),
                Permission(name='Eliminar registros en ' + validated_data['label'], content_type=content_type, codename='delete_custom_' + validated_data['model']),
                Permission(name='Gestionar registros en ' + validated_data['label'], content_type=content_type, codename='manage_custom_' + validated_data['model']),
                Permission(name='Ver gráficos de ' + validated_data['label'], content_type=content_type, codename='graph_custom_' + validated_data['model']),
                Permission(name='Exportar - ' + validated_data['label'], content_type=content_type, codename='export_custom_' + validated_data['model'])
            ]
        )

        return form

    def update(self, instance, validated_data):

        if instance.model == validated_data['model']:
            validated_data.pop('model')
        if validated_data.get('model'):
            # Actualización de permisos del modelo dínamico en caso de que el nombre del formulario cambie
            if instance.model != validated_data.get('model'):
                # Se actualiza el nombre del modelo en la tabla ContentType
                content_type = ContentType.objects.get(app_label="db", model=instance.model)
                try:
                    content_type.model = validated_data.get('model')
                    content_type.save()
                except IntegrityError:
                    raise serializers.ValidationError({ 'label': 'Ya existe un formulario con este nombre' })
                # Se actualiza el modelo del formulario
                dynamic_model = GenerateModel(instance.model)
                dynamic_model.update_model(dynamic_model, instance.model, validated_data['model'])

                # Se obtienen los permisos del formulario que se está editando
                perms = Permission.objects.filter(content_type=content_type.id).order_by('id')
                # Se actualizan permisos
                for i in perms:
                    if 'add_custom_' in i.codename:
                        i.codename = 'add_custom_' + validated_data.get('model')
                        i.name = 'Crear registros en ' + validated_data.get('label')
                    elif 'change_custom_' in i.codename:
                        i.codename = 'change_custom_' + validated_data.get('model')
                        i.name = 'Actualizar registros en ' + validated_data.get('label')
                    elif 'view_custom_' in i.codename:
                        i.codename = 'view_custom_' + validated_data.get('model')
                        i.name = 'Ver registros en ' + validated_data.get('label')
                    elif 'delete_custom_' in i.codename:
                        i.codename = 'delete_custom_' + validated_data.get('model')
                        i.name = 'Eliminar registros en ' + validated_data.get('label')
                    elif 'manage_custom_' in i.codename:
                        i.codename = 'manage_custom_' + validated_data.get('model')
                        i.name = 'Gestionar registros en ' + validated_data.get('label')
                    elif 'graph_custom_' in i.codename:
                        i.codename = 'graph_custom_' + validated_data.get('model')
                        i.name = 'Ver gráficos de ' + validated_data.get('label')
                    elif 'export_custom_' in i.codename:
                        i.codename = 'export_custom_' + validated_data.get('model')
                        i.name = 'Exportar - ' + validated_data.get('label')
                    i.save()

        return super(FormSerializer, self).update(instance, validated_data)

    class Meta:
        model = Form
        fields = '__all__'
        extra_kwargs = {
            'model': { 'required': False, 'read_only': True }
        }
