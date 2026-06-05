from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings

def APIResponse(message="", data=None, status_code=200):
    return Response({
        "status": status_code,
        "message": message,
        "data": data
    }, status=status_code)
    
    

def send_email(subject, message, recipient):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [recipient],
        fail_silently=False
    )