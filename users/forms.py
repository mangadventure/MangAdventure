from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


TextWidget = forms.TextInput(attrs={'class': 'main-bg'})
PassWidget = forms.PasswordInput(attrs={'class': 'main-bg'})


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=150, min_length=6,
                             widget=TextWidget)
    username = forms.CharField(min_length=1, max_length=50,
                               widget=TextWidget)
    password1 = forms.CharField(min_length=8, widget=PassWidget)
    password2 = forms.CharField(min_length=8, widget=PassWidget)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(min_length=1, max_length=50,
                               widget=TextWidget)
    password = forms.CharField(min_length=8, widget=PassWidget)

    class Meta:
        fields = ['username', 'password']


class PassResetForm(forms.Form):
    email = forms.EmailField(min_length=6, max_length=150,
                             widget=TextWidget)

    class Meta:
        fields = ['email']


class SetPassForm(forms.Form):
    password1 = forms.CharField(min_length=8, widget=PassWidget)
    password2 = forms.CharField(min_length=8, widget=PassWidget)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("The passwords don't match!")
        return password2

    class Meta:
        fields = ['password1', 'password2']


__all__ = [
    'RegistrationForm',
    'LoginForm',
    'PassResetForm',
    'SetPassForm',
]

