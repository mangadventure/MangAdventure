from django import forms
from django.contrib.auth.models import User
from django.utils.six import iteritems

from MangAdventure.utils.validators import FileSizeValidator

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    user_id = forms.IntegerField(widget=forms.HiddenInput)

    email = forms.EmailField(
        max_length=150, min_length=6, label='E-mail',
        widget=forms.TextInput(attrs={
            'placeholder': 'E-mail address'
        })
    )
    curr_password = forms.CharField(
        min_length=4, label='Confirm current password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm current password'
        })
    )
    new_password1 = forms.CharField(
        min_length=8, label='New password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New password'
        }), required=False
    )
    new_password2 = forms.CharField(
        min_length=8, label='Confirm new password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password'
        }), required=False
    )

    username = forms.CharField(
        min_length=1, label='Username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username'
        })
    )
    first_name = forms.CharField(
        min_length=1, label='First name',
        widget=forms.TextInput(attrs={
            'placeholder': 'First name'
        }), required=False
    )
    last_name = forms.CharField(
        min_length=1, label='Last name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name'
        }), required=False
    )

    bio = forms.CharField(
        label='About', required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell us a bit about yourself',
            'cols': 35, 'rows': 5
        })
    )

    _validator = FileSizeValidator(max_mb=2)
    avatar = forms.ImageField(
        help_text='Max size: %d MBs' % _validator.max_mb +
                  ' | Optimal dimensions: 300x300',
        widget=forms.FileInput, validators=(_validator,),
        label='Avatar', required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args)
        for key, value in iteritems(kwargs):
            self.fields[key].initial = value
        self.user = User.objects.get(id=self.fields['user_id'].value())

    def clean_username(self):
        username = self.cleaned_data.get('username')
        users = User.objects.filter(username=username)
        if users.exclude(id=self.user_id).count() > 0:
            raise forms.ValidationError('This username is already taken!')
        return username

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 != password2:
            raise forms.ValidationError("The passwords don't match!")
        return password2

    def clean_curr_password(self):
        password = self.cleaned_data.get('curr_password')
        if not self.user.check_password(password):
            raise forms.ValidationError('Wrong password!')
        return password

    def save(self, commit=True):
        self.full_clean()
        prof = UserProfile.objects.get(user_id=self.cleaned_data['user_id'])
        if self.files.get('avatar'):
            prof.avatar = self.files['avatar']
        prof.bio = self.cleaned_data.get('bio')
        prof.user.username = self.cleaned_data.get('username')
        prof.user.first_name = self.cleaned_data.get('first_name')
        prof.user.last_name = self.cleaned_data.get('last_name')
        if self.cleaned_data.get('new_password2'):
            prof.user.set_password(self.cleaned_data['new_password2'])
        if commit:
            prof.save()
        return prof

    class Meta:
        model = UserProfile
        fields = (
            'email', 'new_password1', 'new_password2',
            'username', 'first_name', 'last_name',
            'bio', 'avatar', 'user_id', 'curr_password'
        )


__all__ = ['UserProfileForm']
