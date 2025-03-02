from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_otp_mail_to_email(otp, email):
    try:
        send_mail("OTP for changing password",
                  f"Your OTP is {otp}", "antu.digi.88@gmail.com", [email])  # Send mail
        return "Mail sent successfully"
    except Exception as E:
        return f"Mail failed reason: {str(E)}"


@shared_task
def send_otp_email(email, otp_value):
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp_value}"
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = [email]

    send_mail(subject, message, sender, recipients, fail_silently=False)
    return f"OTP sent to {email}"
