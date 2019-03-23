from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST
from django.contrib.messages import error, info as message
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from allauth.account.models import EmailAddress
from allauth.account.views import LogoutView
from reader.models import Series
from .models import UserProfile, Bookmark
from .forms import UserProfileForm


@login_required
@cache_control(private=True, max_age=3600)
def profile(request):
    uid = request.GET.get('id', request.user.id)
    try:
        prof = UserProfile.objects.get_or_create(user_id=uid)[0]
        if uid != request.user.id and prof.user.is_superuser:
            raise Http404  # hide superuser profile from other users
    except IntegrityError:
        raise Http404
    return render(request, 'profile.html', {'profile': prof})


@login_required
@cache_control(private=True, max_age=0)
def edit_user(request):
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
                message(request, 'Please confirm your new e-mail address.')
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
    return render(request, 'edit_user.html', {'form': form})


class PostOnlyLogoutView(LogoutView):
    def get(self, *args, **kwargs):
        raise Http404


@login_required
@require_POST
def bookmark(request):
    slug = request.POST.get('slug', None)
    series = get_object_or_404(Series, slug=slug)
    try:
        request.user.bookmarks.get(series=series).delete()
    except Bookmark.DoesNotExist:
        request.user.bookmarks.create(user=request.user, series=series)
    return HttpResponse()
