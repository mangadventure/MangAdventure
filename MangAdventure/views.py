from django.shortcuts import render
from constance import config
from api.views import invalid_endpoint
from reader.models import Chapter


def _error_context(msg, status=500):
    return {'error_message': msg, 'error_status': status}


def index(request):
    maximum = config.MAX_RELEASES
    releases = Chapter.objects.all().order_by('-date')[:maximum:1]
    return render(request, 'index.html', {
        'latest_releases': releases,
        'page_url': request.build_absolute_uri()
    })


def handler400(request, exception=None, template_name='error.html'):
    context = _error_context('The server could not '
                             'understand the request.', 400)
    return render(request, template_name=template_name,
                  context=context, status=403)


def handler403(request, exception=None, template_name='error.html'):
    context = _error_context("You don't have permission "
                             "to access this page.", 403)
    return render(request, template_name=template_name,
                  context=context, status=403)


def handler404(request, exception=None, template_name='error.html'):
    if request.path.startswith('/api'):
        return invalid_endpoint(request)
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name=template_name,
                  context=context, status=404)


def handler500(request, exception=None, template_name='error.html'):
    context = _error_context('Whoops! Something went wrong.'
                             ' &macr;\_(&#12484;)_/&macr;')  # Shrug
    return render(request, template_name=template_name,
                  context=context, status=500)

