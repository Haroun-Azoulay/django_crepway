from django.shortcuts import render
from django.db import models
from django.core.mail import EmailMessage, get_connection
from django.conf import settings


def mail(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ["noreply.creepway93@gmail.com"]
        message = request.POST.get("message")
        
        # Check if required fields are filled in
        if subject and email_from and message:
            with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
            ) as connection:
                EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()
                
                
                return render(request, 'mail/success.html')
        
        else
            return render(request, 'mail/error.html')
    
    return render(request, 'mail/mail.html')

def error(request):
    return render(request, 'error.html')

def success(request):
    return render(request, 'success.html')


