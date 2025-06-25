
import pdb
from celery import shared_task
from django.core.cache import cache
from mails.models import EmailCompose, Outbox
from django.db import transaction
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from member.models import Member
import logging
logger = logging.getLogger("myapp")


@shared_task
def delete_email_list_cache():
    try:
        cache.delete_pattern("email_lists::*")
        return "success"
    except Exception as e:
        logger.error(f"Error deleting email list cache: {e}")
        return {"error": str(e)}


# @shared_task
# def bulk_email_send_task(email_compose_id, email_addresses):
#     """
#     Sends bulk emails using the composed template.
#     Logs failed attempts per email.
#     """
#     try:
#         email_compose_obj = EmailCompose.objects.get(id=email_compose_id)
#         email_host_user = email_compose_obj.configurations.username
#         email_host_password = email_compose_obj.configurations.password
#         # Prepare email template
#         context = Context({"test": "test", "member": "test"})
#         template = Template(email_compose_obj.body)
#         rendered_html = template.render(context)

#         with transaction.atomic():
#             success_emails = []
#             failed_emails = []

#             for user_email in email_addresses:
#                 try:
                    
#                     email = EmailMultiAlternatives(
#                         subject=email_compose_obj.subject,
#                         body=rendered_html,
#                         from_email="ahmedsalauddin677785@gmail.com",  # consider environment variable
#                         to=[user_email]
#                     )
#                     email.attach_alternative(rendered_html, "text/html")
#                     email.send()

#                     Outbox.objects.create(
#                         email_compose=email_compose_obj,
#                         status="success",
#                         email_address=user_email
#                     )
#                     success_emails.append(user_email)

#                 except Exception as send_error:
#                     logger.error(
#                         f"Email send failed for {user_email}: {send_error}")
#                     Outbox.objects.create(
#                         email_compose=email_compose_obj,
#                         status="failed",
#                         email_address=user_email,
#                         failed_reason=str(send_error)
#                     )
#                     failed_emails.append((user_email, str(send_error)))

#         return {
#             "success": success_emails,
#             "failed": failed_emails
#         }

#     except Exception as general_error:
#         logger.critical(f"Bulk email task failed: {general_error}")
#         return {"error": str(general_error)}


from django.core.mail import get_connection, EmailMultiAlternatives
from django.template import Context, Template

@shared_task
def bulk_email_send_task(email_compose_id, email_addresses):
    """
    Sends bulk emails using the composed template and dynamic credentials.
    """
    try:
        email_compose_obj = EmailCompose.objects.get(id=email_compose_id)

        email_host_user = email_compose_obj.configurations.username
        email_host_password = email_compose_obj.configurations.password
        if not email_host_user or not email_host_password:
            raise ValueError("Email username or password is missing in configuration.")

        connection = get_connection(
            host='smtp.gmail.com', 
            port=587,
            username=email_host_user,
            password=email_host_password,
            use_tls=True
        )

        # Prepare email body
        context = Context({"test": "test", "member": "test"})
        template = Template(email_compose_obj.body)
        rendered_html = template.render(context)

        success_emails = []
        failed_emails = []

        with transaction.atomic():
            for user_email in email_addresses:
                try:
                    email = EmailMultiAlternatives(
                        subject=email_compose_obj.subject,
                        body=rendered_html,
                        from_email=email_host_user,
                        to=[user_email],
                        connection=connection
                    )
                    email.attach_alternative(rendered_html, "text/html")
                    email.send()

                    Outbox.objects.create(
                        email_compose=email_compose_obj,
                        status="success",
                        email_address=user_email
                    )
                    success_emails.append(user_email)

                except Exception as send_error:
                    logger.error(f"Email send failed for {user_email}: {send_error}")
                    Outbox.objects.create(
                        email_compose=email_compose_obj,
                        status="failed",
                        email_address=user_email,
                        failed_reason=str(send_error)
                    )
                    failed_emails.append((user_email, str(send_error)))

        return {
            "success": success_emails,
            "failed": failed_emails
        }

    except Exception as general_error:
        logger.critical(f"Bulk email task failed: {general_error}")
        return {"error": str(general_error)}
