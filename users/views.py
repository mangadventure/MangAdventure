from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.messages import error, info as message
from django.db import IntegrityError
from django.shortcuts import render
from django.http import Http404, HttpResponse
from allauth.account.models import EmailAddress
from allauth.account.views import LogoutView
from reader.models import Chapter
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
def bookmarks(request):
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
        series = Bookmark.objects.filter(
            user_id=uid
        ).values_list('series', flat=True)
        chapters = Chapter.objects.filter(
            series_id__in=series
        ).order_by('-uploaded')
        return render(request, 'bookmarks.html', {
            'releases': chapters
        })

