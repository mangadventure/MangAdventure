from django.contrib.auth import logout
from .utils import redirect_next


def user_logout(request):
    logout(request)
    return redirect_next(request)
