"""The views of the users app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, info
from django.db import IntegrityError
from django.db.models import Subquery
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic.base import TemplateView

from allauth.account.models import EmailAddress
from allauth.account.views import LogoutView

from MangAdventure.jsonld import breadcrumbs

from reader.models import Chapter

from .forms import UserProfileForm
from .models import Bookmark, UserProfile

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


@login_required
@cache_control(private=True, max_age=3600)
def profile(request: HttpRequest) -> HttpResponse:
    """
    View that serves the profile page of a user.
    A :class:`UserProfile` will be created if it doesn't exist.

    It serves the logged in user's profile by default, but accepts
    an ``id`` query parameter to view an arbitrary user's profile.

    :param request: The original request.

    :return: A response with the rendered ``profile.html`` template.

    :raises Http404: If there is no active user with the specified ``id``.
    """
    try:
        uid = int(request.GET.get('id', request.user.id))
        prof = UserProfile.objects.get_or_create(user_id=uid)[0]
    except (ValueError, IntegrityError) as e:
        raise Http404 from e
    if not prof.user.is_active:  # pragma: no cover
        raise Http404('Inactive user')
    if uid != request.user.id and prof.user.is_superuser:
        raise Http404('Cannot view profile of superuser')
    uri = request.build_absolute_uri(request.path)
    crumbs = breadcrumbs([('User', uri)])
    return render(request, 'profile.html', {
        'profile': prof, 'breadcrumbs': crumbs
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(no_store=True), name='dispatch')
class EditUser(TemplateView):
    """View that serves the edit form for a user's profile."""
    #: The template that this view will render.
    template_name = 'edit_user.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        """
        Initialize attributes shared by all view methods.

        A :class:`~users.models.UserProfile` will be created
        if the request user does not yet have one.

        :param request: The original request.
        """
        super().setup(request)
        if request.user.is_authenticated:
            self.profile = UserProfile.objects \
                .get_or_create(user_id=request.user.id)[0]
            url = request.path
            p_url = url.rsplit('/', 2)[0] + '/'
            crumbs = breadcrumbs([
                ('User', request.build_absolute_uri(p_url)),
                ('Edit', request.build_absolute_uri(url))
            ])
            self.extra_context = {'breadcrumbs': crumbs}

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle ``GET`` requests.

        :param request: The original request.

        :return: A response with the rendered
                 :obj:`template <EditUser.template_name>`.
        """
        form = UserProfileForm(instance=self.profile)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle ``POST`` requests.

        If the user has changed their e-mail,
        a confirmation mail will be sent.

        :param request: The original request.

        :return: A response with the rendered
                 :obj:`template <EditUser.template_name>`.
        """
        form = UserProfileForm(
            request.POST, request.FILES, instance=self.profile
        )
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            if request.user.email != email:
                EmailAddress.objects.add_email(
                    request, request.user, email, confirm=True
                )
                info(request, 'Please confirm your new e-mail address.')
        else:
            error(request, 'Error: please check the fields and try again.')
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(no_store=True), name='dispatch')
class Logout(LogoutView):
    """A :class:`LogoutView` that disallows ``GET`` requests."""
    #: The allowed HTTP methods.
    http_method_names = ('post', 'head', 'options')


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(private=True, max_age=600), name='dispatch')
class Bookmarks(TemplateView):
    """View that serves a user's bookmarks page."""
    #: The template that this view will render.
    template_name = 'bookmarks.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle ``GET`` requests.

        :param request: The original request.

        :return: A response with the rendered
                 :obj:`template <EditUser.template_name>`.
        """
        url = request.path
        p_url = url.rsplit('/', 2)[0] + '/'
        crumbs = breadcrumbs([
            ('User', request.build_absolute_uri(p_url)),
            ('Bookmarks', request.build_absolute_uri(url))
        ])
        chapters = Chapter.objects.filter(series_id__in=Subquery(
            Bookmark.objects.filter(user_id=request.user.id).values('series')
        )).order_by('-published')
        token = UserProfile.objects.only('token') \
            .get_or_create(user_id=request.user.id)[0].token
        return self.render_to_response(self.get_context_data(
            releases=chapters, breadcrumbs=crumbs, token=token
        ))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle ``POST`` requests.

        If a bookmark exists, it will be deleted. If not, it will be created.

        :param request: The original request.

        :return: | An empty :status:`201` response when creating a bookmark.
                 | An empty :status:`204` response when deleting a bookmark.
        """
        bookmark, created = Bookmark.objects.get_or_create(
            user_id=request.user.id, series_id=request.POST.get('series', 0)
        )
        if not created:
            bookmark.delete()
        return HttpResponse(status=(201 if created else 204))


__all__ = ['profile', 'EditUser', 'Bookmarks', 'Logout']
