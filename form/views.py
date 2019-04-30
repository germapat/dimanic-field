from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import serializers as ser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status, serializers, permissions
from rest_framework.response import Response
from app.permissions import HasPermsOnForms, IsExecutiveOrLeader
from .sysmodels import GenerateModel
from .models import *
from .serializers import *
from .defs import permissionsUsers
from app.views import SaveIdUserMixin
from fw.rest.views import ExportModelMixinViewSet
from fw.import_export.resources import BaseResource
import collections, json

User = get_user_model()

class DataViewSet(SaveIdUserMixin, ExportModelMixinViewSet):
    serializer_class = DataSerializer
    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk'):

            # Se obtiene el ID de la URL para consultar el formulario con ese ID y poder trabajar con sus datos
            try:
                self.form = Form.objects.get(id=kwargs['pk'])
            except Form.DoesNotExist:
                raise Http404('Este formulario no existe')

            # Se prepara el modelo
            din = GenerateModel(self.form.model)

            # Se crea el modelo para trabajar con él en el ViewSet
            self.Model = din.model()

            self.queryset = self.Model.objects.filter(deleted=False).order_by('-id')

            self.filterset_class = GenerateModel.get_filter(self.Model, self.form.fields)

            if request.GET.get('ordering'):
                self.queryset = self.queryset.order_by(request.GET.get('ordering'))

            if self.queryset.count() > 0:
                exclude = ['valuesJSON', 'deleted', 'deleted_at', 'form']
                if not self.form.scaling:
                    exclude.extend(['status', 'managementTime', 'currentLevel'])
                self.resource = GenerateModel.get_resources(self.queryset.first(), self.form)(exclude=tuple(exclude))
            else:
                self.resource = BaseResource(model=self.Model)

        else:
            raise Http404('Página no encontrada')

        return super(DataViewSet, self).dispatch(request, *args, **kwargs)

    def export(self, request, **kwargs):
        return super(DataViewSet, self).export(request)

    def get_serializer_context(self):
        return { 'model': self.Model, 'id': self.kwargs.get('pk') }

    def charts(self, request, **kwargs):
        queryset = self.Model.objects.values('valuesJSON')
        json_values = []
        for i in self.form.fields:
            for j in i['fields']:
                if j.get('options'):
                    json_values.append({
                        'label': j.get('label'),
                        'data': [],
                        'chartOptions': {
                            'title': {
                                'text': j.get('name'),
                                'style': {
                                    'fontSize': '12px'
                                }
                            },
                            'legend':{
                                'show': True,
                                'position': 'bottom',
                                'horizontalAlign': 'center',
                                'floating': False,
                                'height': 50,
                                'offsetY': 10
                            },
                            'fill': {
                                'type': 'gradient'
                            },
                            'labels': []
                        }
                    })

        for i in queryset:
            for j in i['valuesJSON']:
                for k in json_values:
                    if k['chartOptions']['title']['text'] == j:
                        # Se recorren los valores para ser unificados y contados
                        if isinstance(i['valuesJSON'][j], list):
                            for l in i['valuesJSON'][j]:
                                k['data'].append(l)
                        else:
                            k['data'].append(i['valuesJSON'][j])
                        labels = []
                        for l in collections.Counter(k['data']).keys():
                            labels.append(l)
                        k['chartOptions']['labels'] = labels

        for i in json_values:
            i['data'] = collections.Counter(i['data']).values()
            i['chartOptions']['title']['text'] = i['chartOptions']['title']['text'].upper().replace('_', ' ')

        return Response({
            'form': self.form.label,
            'charts': json_values
            }, status=status.HTTP_200_OK)

    def config(self, request, **kwargs):
        if self.form.access == 'public':
            serializer = FormSerializer(self.form)
            return Response(serializer.data)
        else:
            if request.user.is_authenticated:
                if request.user.has_perm('db.add_custom_' + self.form.model) or (request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader')):
                    serializer = FormSerializer(self.form)
                    return Response(serializer.data)
                else:
                    return Response({ 'detail': 'No encontrado.' }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({ 'detail': 'Las credenciales de autenticación no se proveyeron.' }, status=status.HTTP_403_FORBIDDEN)

    def list(self, request, **kwargs):
        if request.user.has_perm('db.view_custom_' + self.form.model) or request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader'):
            queryset = self.queryset
            serializer = DataSerializer(queryset, context={'model': self.Model, 'id': self.kwargs.get('pk')})
            return super().list(request, kwargs)
        return Response({ 'detail': 'Las credenciales de autenticación no se proveyeron.' }, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, **kwargs):
        if self.form.access == 'private':
            if request.user.has_perm('db.add_custom_' + self.form.model) or request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader'):
                if self.form.scaling and len(self.form.fields) > 1:
                    request.data['currentLevel'] = self.form.fields[1].get('name')
                return super(DataViewSet, self).create(request, kwargs)
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return super(DataViewSet, self).create(request, kwargs)
    
    def retrieve(self, request, **kwargs):
        if self.form.access == 'private':
            if request.user.has_perm('db.view_custom_' + self.form.model) or request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader'):
                try:
                    queryset = self.Model.objects.get(id=kwargs.get('id_item'), deleted=False)
                except Exception as e:
                    return Response({ 'detail': 'No encontrado.' }, status=status.HTTP_404_NOT_FOUND)
                serializer = DataSerializer(queryset, context={'model': self.Model, 'id': self.kwargs.get('pk')})
                return Response(serializer.data)
            return Response({ 'detail': 'Las credenciales de autenticación no se proveyeron.' }, status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                queryset = self.Model.objects.get(id=kwargs.get('id_item'), deleted=False)
            except Exception as e:
                return Response({ 'detail': 'No encontrado.' }, status=status.HTTP_404_NOT_FOUND)
            serializer = DataSerializer(queryset, context={'model': self.Model, 'id': self.kwargs.get('pk')})
            return Response(serializer.data)

    def update(self, request, **kwargs):
        if request.user.has_perm('db.change_custom_' + self.form.model) or (request.user.has_perm('db.manage_custom_' + self.form.model) or request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader')):
            queryset = self.Model.objects.get(id=kwargs.get('id_item'), deleted=False)
            if not queryset.status == 'finalized':
                if queryset.status == 'in_process' and (request.user.has_perm('db.manage_custom_' + self.form.model) or request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader')):
                    average = ((queryset.managementTime + int(request.data.get('managementTime'))) / 2)
                    queryset.managementTime = round(average)

                    queryset.currentLevel = request.data.get('currentLevel')

                    if request.data.get('valuesJSON'):
                        valuesJSON = request.data.get('valuesJSON')
                        if isinstance(request.data.get('valuesJSON'), str):
                            valuesJSON = json.loads(request.data.get('valuesJSON'))
                        queryset.valuesJSON = valuesJSON

                elif queryset.status == 'joined':
                    valuesJSON = request.data.get('valuesJSON')
                    if isinstance(request.data.get('valuesJSON'), str):
                        valuesJSON = json.loads(request.data.get('valuesJSON'))
                    queryset.valuesJSON = valuesJSON
                else:
                    return Response({ 'detail': 'El registro se encuentra en proceso, por lo tanto no se puede modificar.' }, status=status.HTTP_400_BAD_REQUEST)

                queryset.status = request.data.get('status')
                queryset.updated_by = request.user
                queryset.save()
                return Response(status=status.HTTP_200_OK)
            return Response({ 'detail': 'El registro ya se encuentra finalizado, por lo tanto no se puede modificar.' }, status=status.HTTP_400_BAD_REQUEST)
        return Response({ 'detail': 'Las credenciales de autenticación no se proveyeron.' }, status=status.HTTP_403_FORBIDDEN)

    def disableItem(self, request, **kwargs):
        if request.user.has_perm('db.delete_custom_' + self.form.model) or (request.user.has_perm('db.manage_custom_' + self.form.model) or request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader')):
            try:
                queryset = self.Model.objects.get(id=kwargs.get('id_item'), deleted=False)
            except Exception as e:
                return Response({ 'detail': 'No encontrado.' }, status=status.HTTP_404_NOT_FOUND)
            queryset.deleted = True
            queryset.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def disableForm(self, request, **kwargs):
        if request.user.has_perm('db.delete_custom_' + self.form.model):
            self.form.deleted = True
            self.form.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroyForm(self, request, **kwargs):
        if request.user.has_perm('db.delete_custom_' + self.form.model) or (request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader')):
            try:
                GenerateModel.delete_model(self.Model)
            except Exception as e:
                return Response('No se ha podido eliminar la tabla de la base de datos', status=status.HTTP_400_BAD_REQUEST)
            # try:
            queryset = Form.deletesystem.get(id=kwargs['pk'])
            # except Exception as e:
            #     return Response('No se pudo eliminar registro registro', status=status.HTTP_400_BAD_REQUEST)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)


class FormViewSet(SaveIdUserMixin, viewsets.ModelViewSet):
    serializer_class = FormSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('label', 'description', 'access')
    ordering_fields = ('label', 'description', 'access')
    permission_classes = (HasPermsOnForms|IsExecutiveOrLeader,)

    def initial(self, request, *args, **kwargs):
        self.perms = permissionsUsers(self.request.user.get_all_permissions())
        return super(FormViewSet, self).initial(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        queryset = Form.objects.all().order_by('id')
        form = get_object_or_404(queryset, pk=pk)
        queryset.deleted = True
        queryset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
            En caso de ser Ejecutivo o Líder de equipo, se listan todos los formularios,
            en caso contrario, sólo se listarían los formularios disponibles para ese usuario
            basados en los permisos que tiene.
        """
        if self.request.user.has_perm('pyctivex.executive') or self.request.user.has_perm('pyctivex.leader'):
            return Form.objects.all().order_by('id')
        else:
            return Form.objects.filter(model__in=self.perms).order_by('id')