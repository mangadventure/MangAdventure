def get_user_display(user):
    full_name = user.get_full_name()
    return full_name if len(full_name.strip()) else user.username


default_app_config = 'users.apps.UsersConfig'
