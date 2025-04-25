from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, DeleteAccountForm, ConfirmPasswordForm, AvatarForm, ProfileEditForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Profile, LoginHistory
def send_confirmation_email(request, user):
    uid = urlsafe_base64_encode(str(user.pk).encode())
    token = default_token_generator.make_token(user)
    confirmation_url = request.build_absolute_uri(f'/accounts/confirm/{uid}/{token}/')

    subject = "Подтверждение регистрации"
    message = render_to_string(
        'accounts/activation_email.html',
        {'confirmation_url': confirmation_url}
    )

    send_mail(subject, message, 'from@example.com', [user.email], fail_silently=False)

def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_confirmation_email(request, user)
            messages.success(request, "Вы успешно зарегистрированы! Проверьте ваш email для активации аккаунта.")
            return redirect('index')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                ip_address = request.META.get('REMOTE_ADDR')
                device = request.META.get('HTTP_USER_AGENT', '')
                LoginHistory.objects.create(user=user, ip_address=ip_address, device=device)
                messages.success(request, "Вы успешно вошли в систему!")
                return redirect('index')
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def delete_account(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        password_form = ConfirmPasswordForm(request.POST)
        if form.is_valid() and password_form.is_valid():
            password = password_form.cleaned_data['password']
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                if form.cleaned_data['confirm']:
                    user.delete()
                    logout(request)
                    messages.success(request, "Ваш аккаунт был удален.")
                    return redirect('index')
            else:
                messages.error(request, "Неверный пароль!")
    else:
        form = DeleteAccountForm()
        password_form = ConfirmPasswordForm()

    return render(request, 'accounts/delete_account.html', {'form': form, 'password_form': password_form})

def confirm_registration(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Ваш аккаунт активирован! Теперь вы можете войти.')
        return redirect('login')
    else:
        messages.error(request, 'Неверная ссылка для активации.')
        return redirect('register')


def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш профиль был успешно обновлен!")
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=user_profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})

def change_avatar(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Аватар был обновлен!")
            return redirect('profile')
    else:
        form = AvatarForm(instance=user_profile)

    return render(request, 'accounts/change_avatar.html', {'form': form})
