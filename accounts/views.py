from django.contrib.auth import get_user_model, login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
)
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail 
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        
        if User.objects.filter(username=username).exists():
            error_message = "Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre."
            return render(request, 'accounts/signup.html', {'error_message': error_message})

        if User.objects.filter(email=email).exists():
            error_message = "Cet email est déjà associé à un compte. Veuillez en choisir un autre ou récupérer votre mot de passe."
            return render(request, 'accounts/signup.html', {'error_message': error_message})
        
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('index')

    return render(request, 'accounts/signup.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')

    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('index')


def password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            password_reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(
                'Réinitialisation du mot de passe',
                '',
                'noreply.creepway93@gmail.com',
                [email],
                html_message=f"Bonjour,<br><br>Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le lien ci-dessous pour procéder à la réinitialisation :<br><br><a href='{password_reset_link}'>Réinitialiser le mot de passe</a><br><br>Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet e-mail.<br><br>Cordialement,<br>L'équipe de Crep'Way & Pizza Aulnay-sous-Bois",
            )
            return render(request, 'accounts/password_reset_done.html')

    return render(request, 'accounts/password_reset.html')


def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')