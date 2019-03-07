from django.template.defaultfilters import register
from allauth.socialaccount.models import SocialApp


@register.filter
def available(providers):
    ids = list(map(lambda p: p.id, providers))
    objects = SocialApp.objects \
        .filter(provider__in=ids).values_list('provider', flat=True)
    return list(filter(lambda p: p.id in objects, providers))

