from rest_framework import viewsets, filters, status, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from pyctivex.api import ActiveDirectoryApi
from .models import *
from .serializers import *
from app.permissions import *

User = get_user_model()

@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def user(request):
    perms_map = {
        'POST': ['%(app_label)s.add_%(model_name)s']
    }
    try:
        data = ActiveDirectoryApi.user_data(request.data['user'], ('document', 'first_name', 'last_name', 'surname', 'email', 'boss'))
    except User.DoesNotExist:
        raise ValidationError(_('%(user)s se requiere'), params={'user': request.data['user']}, )
    print(data)
    return Response(data, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        queryset = User.objects.get(is_active=True, id=self.request.user.id)
        serializer = ProfileSerializer(queryset)
        return Response(serializer.data)

    def update(self, request):
        queryset = User.objects.get(is_active=True, id=self.request.user.id)
        serializer = ProfileSerializer(queryset, data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.exclude(is_superuser=True).order_by('-id')
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'login_type',)
    ordering_fields = ('first_name', 'last_name', 'username', 'login_type',)
    permission_classes = (HasPermsOnUsers|IsExecutiveOrLeader,)

    def destroy(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        queryset.is_active = False
        queryset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name',)
    permission_classes = (HasPermsOnGroups|IsExecutiveOrLeader,)

    def get_queryset(self):
        """
            ID 1: Permiso de Ejecutivo
            ID 2: Permiso de Líder de equipo
            ID 3: Permiso de Asesor
            
            Estos permisos son creados por defecto y no se pueden modificar más que por el usuario 'Admin'
        """
        queryset = Group.objects.all()
        if not self.request.user.has_perm('pyctivex.executive'):
            queryset = queryset.exclude(id=1)
        elif not self.request.user.has_perm('pyctivex.executive') and not self.request.user.has_perm('pyctivex.leader'):
            queryset = queryset.exclude(id=1).exclude(id=2)

        return queryset


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.filter(Q(codename__contains='custom') | Q(codename__contains='form') | Q(codename__contains='user')).exclude(Q(codename__contains='log')).order_by('content_type', 'name')
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name',)
    