from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.shortcuts import render


@login_required
@cache_control(private=True, max_age=3600)
def profile(request):
    return render(request, 'profile.html')

