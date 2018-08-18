from django.shortcuts import render


def _error_context(msg, status=500):
    return {'error_message': msg, 'error_status': status}


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
    context = _error_context("Sorry. This page doesn't exist.", 404)
    return render(request, template_name=template_name,
                  context=context, status=404)


def handler500(request, exception=None, template_name='error.html'):
    context = _error_context('Whoops! Something went wrong. ¯\_(ツ)_/¯')
    return render(request, template_name=template_name,
                  context=context, status=500)

