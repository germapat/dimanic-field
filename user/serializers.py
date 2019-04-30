from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from datetime import datetime
from pyctivex.settings import LOGIN_APPLICATION, LOGIN_LDAP
from fw.rest.serializers import BaseModelSerializer
import pprint

User = get_user_model()

class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    user_set = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')
    def __init__(self, *args, **kwargs):
        super(GroupSerializer, self).__init__(*args, **kwargs)

        """
            En caso de que la petición realizada sea por método Get, en lugar de ID's en el caso de campos de relacionados, se mostraría el detalle de cada uno
        """
        if self.context.get('request'):
            if self.context['request'].method.lower() == 'get':
                self.Meta.depth = 1
            else:
                self.Meta.depth = 0

    def to_representation(self, instance):
        representation = super(GroupSerializer, self).to_representation(instance)
        try:
            arrayName = representation['name'].split('_')
            representation['type'] = arrayName[0]
            representation['name'] = arrayName[1]
        except Exception as e:
            representation['name'] = representation['name'].replace('default_', '').replace('custom_', '')
            
        return representation

    def validate_name(self, data):
        if self.context['request'].method.lower() == 'put' and 'default' in self.context['request'].data['type']:
            raise serializers.ValidationError('Este grupo no se puede modificar')
        else:
            return data

    def create(self, validated_data):
        permissions = validated_data.pop('permissions')
        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions')
        instance.name = validated_data['name']
        instance.permissions.set(permissions)
        instance.save()
        return instance

    class Meta:
        model = Group
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if kwargs.get('data'):
            data = kwargs.get('data')
            method = self.context['request'].method.lower()
            if method == 'put' or data.get('login_type') == LOGIN_LDAP:
                self.Meta.extra_kwargs['password']['required'] = False

        if self.context.get('request'):
            if self.context['request'].method.lower() == 'get':
                self.Meta.depth = 1
            else:
                self.Meta.depth = 0

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if representation['login_type'] == 'APPLICATION':
             representation['login'] = 'Aplicación'
        else:
            representation['login'] = 'Directorio activo'
        representation['groupsName'] = []
        return representation

    def create(self, validated_data):
        groups = validated_data.pop('groups')
        user = User.objects.create_user(**validated_data)
        user.groups.set(groups)
        user.user_permissions.set([8, 12])
        return user

    def update(self, instance, validated_data):
        if validated_data.get('groups'):
            groups = validated_data.pop('groups')
            instance.groups.set(groups)
        return super(UserSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'first_name': { 'required': True },
            'email': { 'required': True },
            'last_name': { 'required': True },
            'login_type': { 'required': True },
            'document': { 'required': True },
            'password': { 'write_only': True },
            'user_permissions': { 'read_only': True },
        }

class ProfileSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super(ProfileSerializer, self).to_representation(instance)
        if representation['login_type'] == 'APPLICATION':
             representation['login'] = 'Aplicación'
        else:
            representation['login'] = 'Directorio activo'
        return representation

    def update(self, instance, validated_data):
        if instance.login_type == LOGIN_APPLICATION:
            if validated_data.get('password'):
                password = validated_data.pop('password')
                instance.set_password(password)
            
            return super(ProfileSerializer, self).update(instance, validated_data)
        else:
            raise serializers.ValidationError({ 'password': 'No se puede actualizar la contraseña' })

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'login_type', 'document', 'password')
        extra_kwargs = {
            "username": { 'read_only': True, 'validators': [] },
            'first_name': { 'required': True },
            'last_name': { 'required': True },
            'email': { 'required': True },
            'login_type': { 'read_only': True },
            'password': { 'write_only': True, 'required': False }
        }