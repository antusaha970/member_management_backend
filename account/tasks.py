from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_otp_mail_to_email(otp, email):
    try:
        send_mail("OTP for changing password",
                  f"Your OTP is {otp}", "ahmedsalauddin677785@gmail.com", [email])  # Send mail
        return "Mail sent successfully"
    except Exception as E:
        return f"Mail failed reason: {str(E)}"
