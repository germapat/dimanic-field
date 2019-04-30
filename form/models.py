from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from app.models import Base

User = get_user_model()

####### Modelo contenedor de la información de cada formulario dinámico que se crea. ############
class Form(Base):
    model = models.CharField(verbose_name='Modelo', max_length=200, null=True, unique=True)
    label = models.CharField(verbose_name='Nombre', max_length=200)
    description = models.TextField(verbose_name='Descripción', null=True, blank=True)
    icon = models.CharField(verbose_name='Icono', max_length=200, null=True, blank=True, default="list")
    color = models.CharField(verbose_name='Color', max_length=10, null=True, blank=True, default="#001a7b")

    ACCESS_CHOICES = [('public', 'Público'), ('private', 'Privado')]
    access = models.CharField(verbose_name='Tipo de acceso', default="private", max_length=10, choices=ACCESS_CHOICES)
    scaling = models.BooleanField(verbose_name='Escalamiento', default=False)
    fields = JSONField(default=list, verbose_name='Campos')

    # deletesystem = FormManager()

    class Meta:
        verbose_name_plural = 'Formularios'
        verbose_name = 'Formulario'
        default_permissions = ()
        permissions = (
            ("add_form", "Crear Formularios"),
            ("change_form", "Actualizar Formularios"),
            ("view_form", "Ver Formularios"),
            ("delete_form", "Eliminar Formularios"),
        )