"""The views of the users app."""

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, info
from django.db import IntegrityError
from django.db.models import Subquery
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from allauth.account.models import EmailAddress
from allauth.account.views import LogoutView

from MangAdventure.jsonld import breadcrumbs

from reader.models import Chapter

from .forms import UserProfileForm
from .models import Bookmark, UserProfile

if TYPE_CHECKING:
    from django.http import HttpRequest


@login_required
@cache_control(private=True, max_age=3600)
def profile(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the profile page of a user.
    A :class:`UserProfile` will be created if it doesn't exist.

    It serves the logged in user's profile by default, but accepts
    an ``id`` query parameter to view an arbitrary user's profile.

    :param request: The original request.

    :return: A response with the rendered ``profile.html`` template.

    :raises Http404: If there is no user with the specified ``id``.
    """
    uid = int(request.GET.get('id', request.user.id))
    try:
        prof = UserProfile.objects.get_or_create(user_id=uid)[0]
        if uid != request.user.id and prof.user.is_superuser:
            raise Http404  # hide superuser profile from other users
    except IntegrityError:
        raise Http404
    uri = request.build_absolute_uri(request.path)
    crumbs = breadcrumbs([('User', uri)])
    return render(request, 'profile.html', {
        'profile': prof, 'breadcrumbs': crumbs
    })


@login_required
@cache_control(no_store=True)
def edit_user(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves the edit form for a user's profile.
    A :class:`UserProfile` will be created if it doesn't exist.

    .. admonition:: TODO
       :class: warning

       Convert this to a class-based view.

    :param request: The original request.

    :return: A response with the rendered ``edit_user.html`` template.
    """
    uid = request.user.id
    prof = UserProfile.objects.get_or_create(user_id=uid)[0]
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
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
    else:
        form = UserProfileForm(
            user_id=uid, email=prof.user.email,
            username=prof.user.username,
            first_name=prof.user.first_name,
            last_name=prof.user.last_name,
            bio=prof.bio, avatar=prof.avatar
        )
    url = request.path
    p_url = url.rsplit('/', 2)[0] + '/'
    crumbs = breadcrumbs([
        ('User', request.build_absolute_uri(p_url)),
        ('Edit', request.build_absolute_uri(url))
    ])
    return render(request, 'edit_user.html', {
        'form': form, 'breadcrumbs': crumbs
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(no_store=True), name='dispatch')
class PostOnlyLogoutView(LogoutView):
    """A :class:`LogoutView` that disallows ``GET`` requests."""
    def get(self, *args, **kwargs) -> HttpResponseNotAllowed:
        """
        Handle ``GET`` requests.

        :return: Only ``POST`` requests are allowed.
        """
        return HttpResponseNotAllowed(['POST'])


@login_required
@cache_control(private=True, max_age=3600)
def bookmarks(request: 'HttpRequest') -> HttpResponse:
    """
    View that serves a user's bookmarks page.

    .. admonition:: TODO
       :class: warning

       Convert this to a class-based view.

    :param request: The original request.

    :return: A response with the rendered ``bookmarks.html`` template.
    """
    uid = request.user.id
    if request.method == 'POST':
        sid = request.POST.get('series', 0)
        try:
            Bookmark.objects.get(user_id=uid, series_id=sid).delete()
            return HttpResponse(status=204)
        except Bookmark.DoesNotExist:
            Bookmark.objects.create(user_id=uid, series_id=sid)
            return HttpResponse('Created bookmark')
    else:
        chapters = Chapter.objects.filter(series_id__in=Subquery(
            Bookmark.objects.filter(user_id=uid).values('series')
        )).order_by('-uploaded')
        url = request.path
        p_url = url.rsplit('/', 2)[0] + '/'
        crumbs = breadcrumbs([
            ('User', request.build_absolute_uri(p_url)),
            ('Bookmarks', request.build_absolute_uri(url))
        ])
        return render(request, 'bookmarks.html', {
            'releases': chapters, 'breadcrumbs': crumbs
        })


__all__ = ['profile', 'edit_user', 'bookmarks', 'PostOnlyLogoutView']
