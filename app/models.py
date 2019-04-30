from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Base(models.Model):
    created_at = models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por', null=True, blank=True, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(verbose_name='Fecha de actualización', auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Actualizado por', null=True, blank=True, related_name='%(app_label)s_%(class)s_updated_by')
    deleted = models.BooleanField(verbose_name='Eliminado', default=False)
    deleted_at = models.DateTimeField(verbose_name='Fecha eliminación', null=True, blank=True)

    class Meta:
        abstract = True