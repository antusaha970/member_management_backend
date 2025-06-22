from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class MailBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class SMTPConfiguration(MailBaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)  # r
    provider = models.CharField(max_length=50, choices=[
        ('gmail', 'Gmail'),
        ('personal', 'Personal Domain'),
        ('ses', 'Amazon SES'),
    ], default="gmail")  # r
    host = models.CharField(max_length=255, blank=True, null=True)  # r
    port = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    password = models.CharField(max_length=255, null=True, blank=True)
    use_tls = models.BooleanField(default=True, null=True, blank=True)
    use_ssl = models.BooleanField(default=False, null=True, blank=True)
    aws_access_key_id = models.CharField(
        max_length=255, null=True, blank=True)  # r
    aws_secret_access_key = models.CharField(
        max_length=255, null=True, blank=True)  # r
    aws_region = models.CharField(max_length=50, null=True, blank=True)
    ses_configuration_set = models.CharField(
        max_length=255, null=True, blank=True)
    iam_role_arn = models.CharField(max_length=255, null=True, blank=True)
    enable_tracking = models.BooleanField(default=False)

    # relations
    user = models.ForeignKey(User, related_name="user_smtp_configs",
                             on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.username


class Email_Compose(MailBaseModel):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    configurations = models.ForeignKey(
        SMTPConfiguration, on_delete=models.SET_NULL, null=True, blank=True)

    # relations
    user = models.ForeignKey(User, related_name="user_composes",
                             on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.subject


class EmailAttachment(MailBaseModel):
    file = models.FileField(upload_to="attachmentsFiles/")
    email_compose = models.ForeignKey(Email_Compose, on_delete=models.CASCADE)

    def __str__(self):
        return self.email_compose.subject


STATUS_CHOICES = [
    ('success', 'Success'),
    ('failed', 'Failed'),
    ('pending', 'Pending'),
]


class Outbox(MailBaseModel):
    email_address = models.EmailField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    email_compose = models.ForeignKey(Email_Compose, on_delete=models.CASCADE)
    failed_reason = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    def __str__(self):
        return self.email_address
