from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.utils.encoding import force_text, force_bytes
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.conf import settings
from base64 import b64decode, b64encode
from constance import config
from .tokens import activation_token, InvalidTokenError
from .forms import (
    RegistrationForm, LoginForm,
    PassResetForm, SetPassForm
)
from .utils import (
    reverse_query, safe_mail, redirect_next,
    RESET_TEMPLATE, ACTIVATE_TEMPLATE
)
from .models import User


def make_token(user):
    token = activation_token.make_token(user)
    return b64encode(force_bytes(token)).decode()


def parse_token(token):
    return force_text(b64decode(token))


def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            email = form.cleaned_data['email']
            EmailMessage(
                from_email=settings.DEFAULT_FROM_EMAIL,
                subject='[%s] Account activation' % config.NAME,
                body=ACTIVATE_TEMPLATE.format(
                    username=user.username or 'user',
                    name=config.NAME or 'our site',
                    scheme='https' if request.is_secure() else 'http',
                    domain=get_current_site(request).domain,
                    url=reverse_query('users:activate', query={
                        'token': make_token(user), 'uid': user.pk
                    })
                ),
                to=[safe_mail(email)],
            ).send()
            response = ' '.join[
                'We have sent you an activation link to',
                'the email address you provided. Click',
                'that link to complete your registration.']
            return render(request, 'activate.html', {
                'title': 'Activation Pending',
                'response': response
            })
    return render(request, 'register.html', {'form': form})


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect_next(request)
    return render(request, 'login.html', {'form': form})


def activate(request):
    try:
        uid = request.GET.get('uid')
        token = parse_token(request.GET.get('token'))
        user = User.objects.get(pk=uid)
        if not activation_token.check_token(user, token):
            raise InvalidTokenError
    except(TypeError, ValueError,
           User.DoesNotExist,
           InvalidTokenError):
        response = 'Error: You seem to have ' \
            'followed an invalid activation link.'
    else:
        user.is_active = True
        user.save()
        login(request, user)
        response = 'Your account has been successfully activated.'
    return render(request, 'activate.html', {
        'title': 'Account Activation',
        'response': response
    })


def user_logout(request):
    logout(request)
    return redirect_next(request)


def pass_reset(request):
    form = PassResetForm()
    if request.method == 'POST':
        if request.POST.get('uid'):
            return pass_new(request)
        form = PassResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'pass_reset.html', {
                    'form': None, 'email': email, 'exists': False
                })
            else:
                EmailMessage(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    subject='[%s] Password reset' % config.NAME,
                    body=RESET_TEMPLATE.format(
                        username=user.username or 'user',
                        name=config.NAME or 'our site',
                        scheme='https' if request.is_secure() else 'http',
                        domain=get_current_site(request).domain,
                        url=reverse_query('users:reset', query={
                            'token': make_token(user), 'uid': user.pk
                        })
                    ),
                    to=[safe_mail(email)],
                ).send()
                return render(request, 'pass_reset.html', {
                    'form': None, 'email': email, 'exists': True
                })
    if {'uid', 'token'} <= set(request.GET):
        return pass_new(request)
    return render(request, 'pass_reset.html', {
        'form': form, 'email': None
    })


def pass_new(request):
    form = SetPassForm()
    valid = True
    if request.method == 'POST':
        form = SetPassForm(request.POST)
        uid = request.POST.get('uid')
        if form.is_valid():
            password = form.cleaned_data['password1']
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            return render(request, 'pass_reset.html', {
                'form': None, 'email': None
            })
    try:
        uid = request.GET.get('uid')
        token = parse_token(request.GET.get('token'))
        user = User.objects.get(pk=uid)
        if not activation_token.check_token(user, token):
            raise InvalidTokenError
    except(TypeError, ValueError,
           User.DoesNotExist,
           InvalidTokenError):
        valid = False
        form = None
    return render(request, 'pass_new.html', {
        'form': form, 'valid': valid
    })

