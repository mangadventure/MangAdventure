from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from constance import config
from .forms import *
from .tokens import activation_token


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
                from_email="register@arc-relight.site",
                subject="Activate your {} account.".format(config.NAME),
                body=render_to_string('activation_email.html', {
                    'user': user,
                    'domain':  get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': activation_token.make_token(user),
                }),
                to=[email],
            ).send()
            return activate_prompt(request, email)

    return render(request, 'register.html', {'form': form})


def userlogin(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('index')

    return render(request, 'login.html', {'form': form})


def activate_prompt(request, email):
    return render(request, 'activate_prompt.html', {'email': email})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, User.DoesNotExist):
        user = None
    if user is not None and activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        response = "Successfully activated your email."
    else:
        response = "Invalid activation link."

    return render(request, 'activate_reply.html', {'response': response})


def userlogout(request):
    logout(request)

    return redirect('index')


def reset_prompt(request):
    form = PassResetForm()
    if request.method == 'POST':
        form = PassResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            if user:
                EmailMessage(
                    from_email="register@arc-relight.site",
                    subject="Password reset on {}".format(config.NAME),
                    body=render_to_string('reset_email.html', {
                        'user': user,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                        'token': activation_token.make_token(user),
                    }),
                    to=[email],
                ).send()
            return reset_prompt_success(request, email)

    return render(request, 'reset_prompt.html', {'form': form})


def reset_prompt_success(request, email):
    return render(request, 'reset_prompt_done.html', {'email': email})


def reset(request, uidb64, token):
    form = SetPassForm()
    if request.method == 'POST':
        form = SetPassForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            return pass_reset_success(request)

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, User.DoesNotExist):
        user = None
    if user is not None and activation_token.check_token(user, token):
        valid = True
    else:
        form = None
        valid = False

    return render(request, 'reset_pass.html', {'form': form, 'valid': valid, 'uid': uidb64, 'token': token})


def pass_reset_success(request):
    return render(request, 'reset_done.html')
