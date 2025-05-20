from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile

# Форма для подтверждения пароля
class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label="Введите свой пароль для подтверждения")

# Форма для изменения пароля
class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(), label="Старый пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput(), label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput(), label="Подтверждение нового пароля")

# Форма редактирования профиля пользователя
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'avatar']

# Форма регистрации пользователя
class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Форма для входа в систему
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

# Форма для подтверждения удаления аккаунта
class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Подтвердите удаление аккаунта")

# Форма для изменения аватара пользователя
class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

# Форма для изменения email пользователя
class EmailForm(forms.Form):
    email = forms.EmailField(label='Введите ваш email', max_length=100)
