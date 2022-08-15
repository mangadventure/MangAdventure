"""Form models for the users app."""

from typing import cast

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator

from MangAdventure.validators import FileSizeValidator

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Form used for editing a :class:`~users.models.UserProfile` model."""
    #: The user's e-mail address.
    email = forms.EmailField(
        max_length=254, min_length=5, label='E-mail',
        widget=forms.TextInput(attrs={
            'placeholder': 'E-mail address'
        })
    )
    #: The current password of the user.
    curr_password = forms.CharField(
        min_length=8, label='Confirm current password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm current password'
        })
    )
    #: The new password of the user.
    new_password1 = forms.CharField(
        min_length=8, label='New password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New password'
        }), required=False
    )
    #: The new password of the user again.
    new_password2 = forms.CharField(
        min_length=8, label='Confirm new password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password'
        }), required=False
    )

    #: The username of the user.
    username = forms.CharField(
        min_length=1, label='Username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username'
        }), max_length=150, validators=(
            UnicodeUsernameValidator(),
        )
    )
    #: The user's first name.
    first_name = forms.CharField(
        label='First name', required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name'
        }), max_length=150
    )
    #: The user's last name.
    last_name = forms.CharField(
        label='Last name', required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name'
        }), max_length=150
    )

    #: The user's bio.
    bio = forms.CharField(
        label='About', required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell us a bit about yourself',
            'cols': 35, 'rows': 5
        })
    )

    #: The user's avatar.
    avatar = forms.ImageField(
        help_text='Max size: 2 MBs | Optimal dimensions: 300x300',
        label='Avatar', required=False, widget=forms.FileInput,
        validators=(FileSizeValidator(max_mb=2),),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['avatar'].initial = self.instance.avatar
            self.fields['bio'].initial = self.instance.bio

    def clean_username(self) -> str:
        """
        Validate the chosen username.

        :return: The username if valid.

        :raises ValidationError: If the username is taken.
        """
        username = self.cleaned_data.get('username')
        users = User.objects.filter(username=username)
        if users.exclude(id=self.instance.user_id).exists():
            raise forms.ValidationError('This username is already taken!')
        return cast(str, username)

    def clean_new_password2(self) -> str:
        """
        Validate the chosen password.

        :return: The new password if valid.

        :raises ValidationError: If the passwords don't match.
        """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 != password2:
            raise forms.ValidationError("The passwords don't match!")
        return cast(str, password2)

    def clean_curr_password(self) -> str:
        """
        Validate the current password.

        :return: The current password if valid.

        :raises ValidationError: If the password is wrong.
        """
        password = self.cleaned_data.get('curr_password')
        if not self.instance.user.check_password(password):
            raise forms.ValidationError('Wrong password!')
        return cast(str, password)

    def save(self, commit: bool = True) -> UserProfile:
        """
        Save the changes to the :class:`UserProfile`.

        :param commit: Controls whether the changes
                       should be committed to the database.

        :return: The updated ``UserProfile`` object.
        """
        self.full_clean()
        if self.files.get('avatar'):
            self.instance.avatar = self.files['avatar']
        self.instance.bio = self.cleaned_data.get('bio')
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.username = self.cleaned_data.get('username')
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        if self.cleaned_data.get('new_password2'):
            self.instance.user.set_password(self.cleaned_data['new_password2'])
        if commit:
            self.instance.save()
            self.instance.user.save()
        return self.instance

    class Meta:
        model = UserProfile
        fields = (
            'email', 'new_password1', 'new_password2',
            'username', 'first_name', 'last_name',
            'bio', 'avatar', 'curr_password'
        )


__all__ = ['UserProfileForm']
