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


__all__ = [
    'reverse',
    'reverse_query',
    'redirect_next',
    'safe_mail',
]

