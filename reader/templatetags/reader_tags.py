from django.template.defaultfilters import register


@register.filter
def preload_pages(pages, num):
    return list(filter(
        lambda p: p.number > num and p.number < (num + 4), pages
    ))
