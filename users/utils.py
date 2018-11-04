from django.utils.http import urlencode
from django.shortcuts import redirect
from django.urls import reverse


def reverse_query(view, **kwargs):
    query = kwargs.pop('query', {})
    url = reverse(view, **kwargs)
    return '%s?%s' % (url, urlencode(query))


def redirect_next(request, default='index'):
    return redirect(request.GET.get('next', default))


# https://docs.djangoproject.com/en/2.1/topics/email/#preventing-header-injection
def safe_mail(eml):
    return eml.replace('\r', '').replace('\n', '')


RESET_TEMPLATE = """\
Dear {username},

You have requested to reset your password on {name}.
To do so, please click the link below.
If you didn't make this request, ignore this email.

{scheme}://{domain}{url}
"""

ACTIVATE_TEMPLATE = """\
Dear {username},

Thank you for registering to {name}.
Please click the following link to activate your account:

{scheme}://{domain}{url}
"""

__all__ = [
    'reverse',
    'reverse_query',
    'redirect_next',
    'safe_mail',
    'RESET_TEMPLATE',
    'ACTIVATE_TEMPLATE',
]

