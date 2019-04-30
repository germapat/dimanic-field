from django.contrib.auth.models import Permission
from rest_framework import permissions
from pprint import pprint

class IsExecutive(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('pyctivex.executive'):
            return True
        else:
            return False

class IsLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('pyctivex.leader'):
            return True
        else:
            return False

class IsExecutiveOrLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader'):
            return True
        else:
            return False

class IsExecutiveAndLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('pyctivex.executive') and request.user.has_perm('pyctivex.leader'):
            return True
        else:
            return False

"""
    Permisos para la tabla de usuarios
"""
class HasPermsOnUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.has_perm('pyctivex.list_user') or request.user.has_perm('pyctivex.retrieve_user'):
                return True
            else:
                return False
        elif request.method == 'PUT':
            if request.user.has_perm('pyctivex.change_user'):
                return True
            else:
                return False
        elif request.method == 'POST':
            if request.user.has_perm('pyctivex.add_user'):
                return True
            else:
                return False
        elif request.method == 'DELETE':
            if request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader'):
                return True
            else:
                return False

"""
    Permisos para la tabla de grupos
"""
class HasPermsOnGroups(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.is_authenticated:
                return True
            else:
                return False
        elif request.method == 'PUT':
            if request.user.has_perm('pyctivex.change_groups'):
                return True
            else:
                return False
        elif request.method == 'POST':
            if request.user.has_perm('pyctivex.add_groups'):
                return True
            else:
                return False
        elif request.method == 'DELETE':
            if request.user.has_perm('pyctivex.executive') or request.user.has_perm('pyctivex.leader'):
                return True
            else:
                return False

"""
    Permisos para la tabla de formularios
"""
class HasPermsOnForms(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.has_perm('form.view_form'):
                return True
            else:
                return False
        elif request.method == 'PUT':
            if request.user.has_perm('form.change_form'):
                return True
            else:
                return False
        elif request.method == 'POST':
            if request.user.has_perm('form.add_form'):
                return True
            else:
                return False
        elif request.method == 'DELETE':
            if request.user.has_perm('form.delete_form'):
                return True
            else:
                return False