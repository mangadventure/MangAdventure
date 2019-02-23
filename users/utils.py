def user_display(user):
    full_name = user.get_full_name()
    return full_name if len(full_name.strip()) > 0 else user.username

