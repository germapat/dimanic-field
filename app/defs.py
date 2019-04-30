'''
    Para ingresar esta información inicial se debe de seguir la siguiente configuración:

    En la carpeta "migrations/" en el archivo inicial, por lo general tiene incluído en su nombre la palabra "initial" incluir las siguientes líneas de código:

    from app.defs import initial_data

    operations = [
        migrations.RunPython(initial_data)
    ]
'''

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission 
from django.contrib.contenttypes.models import ContentType 
from e_survey.settings.base import PERMISSIONS, GROUPS

User = get_user_model()

# Crea datos iniciales durante la primera migración del proyecto
def initial_data(apps, schema_editor):
    content_type = ContentType.objects.get_for_model(User)
    db_alias = schema_editor.connection.alias

    # Se crean permisos
    perm_executive = Permission.objects.using(db_alias).create(name=PERMISSIONS['EXECUTIVE'], content_type=content_type, codename=PERMISSIONS['EXECUTIVE'])
    perm_leader = Permission.objects.using(db_alias).create(name=PERMISSIONS['LEADER'], content_type=content_type, codename=PERMISSIONS['LEADER'])
    perm_agent = Permission.objects.using(db_alias).create(name=PERMISSIONS['AGENT'], content_type=content_type, codename=PERMISSIONS['AGENT'])

    # Se crean grupos
    group_executive = Group.objects.using(db_alias).create(name=GROUPS['EXECUTIVE'])
    group_leader = Group.objects.using(db_alias).create(name=GROUPS['LEADER'])
    group_agent = Group.objects.using(db_alias).create(name=GROUPS['AGENT'])

    # Se agregan permisos a los grupos
    group_executive.permissions.add(perm_executive)
    group_leader.permissions.add(perm_leader)
    group_agent.permissions.add(perm_agent)

    # Se crea usuario Admin
    superuser = User.objects.create(username="admin", document="000000000", is_superuser=True, is_staff=True, login_type="APPLICATION", first_name="Administrador")
    superuser.set_password('a123')
    superuser.save()