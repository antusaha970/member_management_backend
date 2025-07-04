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
        ('gmail', 'gmail'),
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


class EmailCompose(MailBaseModel):
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
    email_compose = models.ForeignKey(
        EmailCompose, on_delete=models.CASCADE, related_name="email_compose_attachments")

    def __str__(self):
        return self.email_compose.subject


STATUS_CHOICES = [
    ('success', 'success'),
    ('failed', 'failed'),
    ('pending', 'pending'),
]


class Outbox(MailBaseModel):
    email_address = models.EmailField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    email_compose = models.ForeignKey(
        EmailCompose, on_delete=models.CASCADE, null=True, blank=True, related_name="outbox_email_composes")
    failed_reason = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    is_from_template = models.BooleanField(default=False)

    def __str__(self):
        return self.email_address


class EmailGroup(MailBaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=500, default='', blank=True)
    # relations
    user = models.ForeignKey(
        User, related_name="user_email_groups", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class EmailList(MailBaseModel):
    email = models.EmailField(max_length=255)
    is_subscribed = models.BooleanField(default=True)
    # relations
    group = models.ForeignKey(
        EmailGroup, related_name="group_email_lists", on_delete=models.CASCADE)
    class Meta:
        unique_together = ('email', 'group')
        
    def __str__(self):
        return self.email


class SingleEmail(MailBaseModel):
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return self.email


class EmailSendRecord(models.Model):
    schedule_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    # ForeignKey relations
    email_compose = models.ForeignKey(
        EmailCompose, on_delete=models.CASCADE, related_name='email_compose_sends')
    group = models.ForeignKey(
        EmailGroup, on_delete=models.CASCADE, related_name='email_group_sends', null=True, blank=True
    )
    single_email = models.ForeignKey(
        SingleEmail, on_delete=models.CASCADE, related_name='email_single_sends', null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if bool(self.group) == bool(self.single_email):
            raise ValueError(
                "Assign either group or single_email, not both or none.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"EmailSend object {self.pk}"
