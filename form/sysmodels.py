from app.models import Base
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models, connection
from django_filters import rest_framework as filters
from rest_framework import serializers
from fw.import_export.resources import BaseResource
from fw.rest.serializers import BaseModelSerializer
from import_export import resources, fields, widgets
from .models import *
import json

class GenerateModel:

    def __init__(self, name):
        self.tbl_name = name
        self.app_label = 'db'

    # Prepara la estructura del modelo
    def model(self):

        class Meta:
            pass

        setattr(Meta, 'app_label', self.app_label)

        attrs = {
            '__module__': '',
            'Meta': Meta
        }

        fields = {}
        fields['form'] = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, editable=False, verbose_name='Valores dinámicos')
        JOINED = 'joined'
        IN_PROCESS = 'in_process'
        FINALIZED = 'finalized'
        STATUS_CHOICES = ((JOINED, 'Ingresado'), (IN_PROCESS, 'En proceso'), (FINALIZED, 'Finalizado'),)
        fields['managementTime'] = models.PositiveIntegerField(verbose_name='Tiempo promedio de gestión', null=True, default=0)
        fields['status'] = models.CharField(verbose_name='Estado', max_length=200, choices=STATUS_CHOICES, null=True, default=JOINED)
        fields['currentLevel'] = models.CharField(verbose_name='Nivel actual', max_length=200, null=True, blank=True)
        fields['valuesJSON'] = JSONField()

        attrs.update(fields)
        return type(self.tbl_name, (Base,), attrs)

    def get_resources(instance, form):

        attrs = {}
            
        attrs['created_at'] = fields.Field(
            attribute="created_at",
            column_name="Fecha de creación",
            readonly=True,
            widget=widgets.DateTimeWidget(format="%d-%m-%Y %H:%M:%S")
        )
        
        attrs['updated_at'] = fields.Field(
            attribute="updated_at",
            column_name="Fecha de actualizado",
            readonly=True,
            widget=widgets.DateTimeWidget(format="%d-%m-%Y %H:%M:%S")
        )
        attrs['updated_by'] = fields.Field(
            attribute="updated_by",
            column_name="Actualizado por",
            readonly=True,
        )

        for i in instance.valuesJSON:
            attrs[i] = fields.Field(column_name=i,)

            def dehydrate(self, model, j=i):
                data = ''
                if model.valuesJSON.get(j):
                    data = model.valuesJSON[j]
                else:
                    data = ''
                return data

            attrs['dehydrate_{}'.format(i)] = dehydrate


        return type('DataResources', (BaseResource,), attrs)

    ## Crea el modelo
    def create_model(self):

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(self.model())

    def update_model(self, model, oldName, newName):

        with connection.schema_editor() as schema_editor:
            schema_editor.alter_db_table(model, self.app_label + '_' + oldName, self.app_label + '_' + newName)

        self.tbl_name = newName

    def delete_model(model):

        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(model)

    def get_filter(model, campos):

        class Meta:
            pass

        fields = {}
        array = []
        fields['id'] = filters.CharFilter(label='ID', lookup_expr='icontains')
        fields['created_by__username'] = filters.CharFilter(label='Creado por', lookup_expr='icontains')
        fields['created_at'] = filters.CharFilter(label='Fecha de creación', lookup_expr='icontains')
        fields['updated_by'] = filters.CharFilter(label='Actualizado por', lookup_expr='icontains')
        fields['updated_at'] = filters.CharFilter(label='Fecha de actualización', lookup_expr='icontains')
        fields['status'] = filters.CharFilter(label='Estado', lookup_expr='icontains')
        array.append('id')
        array.append('created_by__username')
        array.append('created_at')
        array.append('updated_by')
        array.append('updated_at')
        array.append('status')
        for i in campos:
            for j in i['fields']:
                name = 'valuesJSON__{}'.format(j['name'])
                fields[name] = filters.CharFilter(label=j['name'], lookup_expr='icontains')
                array.append(name)
        setattr(Meta, 'model', model)
        setattr(Meta, 'fields', array)
        attrs = {
            '__module__': '',
            'Meta': Meta
        }

        attrs.update(fields)

        return type('DataFilter', (filters.FilterSet,), attrs)