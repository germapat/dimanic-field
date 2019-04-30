import collections

def permissionsUsers(user):
    perms = []
    for i in user:
        if 'db.' in i:
            if 'db.add_custom_' in i:
                perms.append(i.split('db.add_custom_')[1])
            elif 'db.change_custom_' in i:
                perms.append(i.split('db.change_custom_')[1])
            elif 'db.view_custom_' in i:
                perms.append(i.split('db.view_custom_')[1])
            elif 'db.delete_custom_' in i:
                perms.append(i.split('db.delete_custom_')[1])
    return collections.Counter(perms).keys()
