
import os
from django.template import Context, Template
from django.core.mail import get_connection, EmailMultiAlternatives
import pdb
from celery import shared_task
from django.core.cache import cache
from mails.models import EmailCompose, Outbox
from django.db import transaction
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from member.models import Member, Email
from django.template.loader import render_to_string
from django.conf import settings
import logging
logger = logging.getLogger("myapp")


@shared_task
def bulk_email_send_task(email_compose_id, email_addresses):
    """
    Sends bulk emails with optional attachments using a composed template.
    Efficient database operations and attachment existence check added.
    """
    try:
        if not email_addresses or not isinstance(email_addresses, list):
            raise ValueError("Email addresses must be a non-empty list.")

        email_compose_obj = EmailCompose.objects.select_related('configurations')\
            .prefetch_related('email_compose_attachments').get(id=email_compose_id)

        attachments = email_compose_obj.email_compose_attachments.all()
        email_host_user = email_compose_obj.configurations.username
        email_host_password = email_compose_obj.configurations.password

        if not email_host_user or not email_host_password:
            raise ValueError(
                "Email username or password is missing in configuration.")

        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username=email_host_user,
            password=email_host_password,
            use_tls=True
        )

        # Prepare the rendered HTML body
        context = Context({"test": "test12345", "member": "arifin"})
        template = Template(email_compose_obj.body)
        rendered_html = template.render(context)

        success_emails = []
        failed_emails = []
        outbox_list = []

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

                for attachment in attachments:
                    file_path = attachment.file.path
                    file_name = attachment.file.name
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            email.attach(os.path.basename(file_name), f.read())
                    else:
                        logger.warning(
                            f"Attachment file not found: {file_path}")

                email.send()
                success_emails.append(user_email)

                outbox_list.append(Outbox(
                    email_compose=email_compose_obj,
                    status="success",
                    email_address=user_email
                ))

            except Exception as send_error:
                logger.error(
                    f"Email send failed for {user_email}: {send_error}")
                failed_emails.append((user_email, str(send_error)))
                outbox_list.append(Outbox(
                    email_compose=email_compose_obj,
                    status="failed",
                    email_address=user_email,
                    failed_reason=str(send_error)
                ))

        #  Bulk insert outbox records in batches
        try:
            with transaction.atomic():
                for i in range(0, len(outbox_list), 100):
                    Outbox.objects.bulk_create(outbox_list[i:i+100])
        except Exception as db_err:
            logger.critical(f"Bulk create failed: {db_err}")
            return {"error": str(db_err)}

        return {
            "success": success_emails,
            "failed": failed_emails
        }

    except Exception as general_error:
        logger.critical(f"Bulk email task failed: {general_error}")
        return {"error": str(general_error)}


@shared_task
def send_monthly_member_emails():
    members = Member.objects.filter(is_active=True)
    try:
        outbox_list = []
        for member in members:
            try:
                email_list = Email.objects.filter(
                    member=member).order_by("-is_primary").first()
                to_email = email_list.email if email_list else None
                if to_email:
                    html_message = render_to_string('mails/member_mail_template.html', {
                        'member_ID': member.member_ID,
                        'first_name': member.first_name,
                        'last_name': member.last_name,
                        'date_of_birth': member.date_of_birth,
                        'batch_number': member.batch_number,
                        'anniversary_date': member.anniversary_date,
                        'blood_group': member.blood_group,
                        'nationality': member.nationality,
                    })
                    msg = EmailMultiAlternatives(
                        subject="Your Monthly Member Update",
                        body="This is your monthly profile update.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[to_email]
                    )
                    msg.attach_alternative(html_message, "text/html")
                    msg.send()
                    outbox_list.append(Outbox(email_address=to_email,
                                              status="success",
                                              is_from_template=True))
            except Exception as e:
                outbox_list.append(Outbox(email_address=to_email,
                                          status="failed",
                                          failed_reason=str(e),
                                          is_from_template=True))

        for i in range(0, len(outbox_list), 100):
            Outbox.objects.bulk_create(outbox_list[i:i+100])
        return {"status": True, "description": "All mail has been sent"}
    except Exception as e:
        print(e)
        print("Something went wrong!! ", str(e))
        return {"status": False, "description": "Something went wrong while sending mail", "error": str(e)}



@shared_task
def retry_failed_emails():
    try:
        cache.set("mails::retry", True)
        failed_mails = Outbox.objects.select_related("email_compose").filter(status="failed")
        
        if not failed_mails.exists():
            return {"status": "failed", "description": "No failed emails found to retry"}
        
        outbox_list = []
        success_count = 0
        fail_count = 0

        for mail in failed_mails:
            try:
                compose = mail.email_compose
                attachments = compose.email_compose_attachments.all()
                if not compose:
                    continue

                subject = compose.subject
                body = compose.body
                email_address = mail.email_address
                config = compose.configurations

                if not config:
                    continue

                username = config.username
                password = config.password
               

                # Setup email connection
                connection = get_connection(
                    host='smtp.gmail.com',
                    port=587,
                    username=username,
                    password=password,
                    use_tls=True
                )

                # Render template
                context = Context({})
                template = Template(body)
                rendered_html = template.render(context)
                
                # Prepare email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=rendered_html,
                    from_email=username,
                    to=[email_address],
                    connection=connection
                )

                for attachment in attachments:
                    file_path = attachment.file.path
                    file_name = attachment.file.name
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            email.attach(os.path.basename(file_name), f.read())
                    else:
                        logger.warning(
                            f"Attachment file not found: {file_path}")

                email.attach_alternative(rendered_html, "text/html")
                
                # Send email
                email.send()

                # Success
                mail.status = "success"
                mail.failed_reason = None
                success_count += 1
                outbox_list.append(mail)

            except Exception as e:
                # Failure
                mail.status = "failed"
                mail.failed_reason = str(e)
                fail_count += 1
                outbox_list.append(mail)

        # Bulk update database
        for i in range(0, len(outbox_list), 100):
            Outbox.objects.bulk_update(outbox_list[i:i+100], ["status", "failed_reason"])

        # Final result
        if success_count == 0:
            return {"status":"failed", "description": "No mail was sent", "failed": fail_count}
        elif fail_count > 0:
            return {
                "status": "partial",
                "description": f"{success_count} succeeded, {fail_count} failed",
            }
        else:
            return {"status": "success", "description": "All mails sent successfully"}

    except Exception as e:
        return {"status": "failed", "description": "Something went wrong", "error": str(e)}
    finally:
        cache.delete("mails::retry")
