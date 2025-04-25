from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'avatar']

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Подтвердите удаление аккаунта")

class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label="Введите свой пароль для подтверждения")

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
