from rest_framework import serializers
from .models import *
from collections import Counter
import re

class SMTPConfigurationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    provider = serializers.CharField(max_length=50)
    host = serializers.CharField(max_length=255, required=False)
    port = serializers.IntegerField(required=False)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    use_tls = serializers.BooleanField(required=False)
    use_ssl = serializers.BooleanField(required=False)
    aws_access_key_id = serializers.CharField(max_length=255, required=False)
    aws_secret_access_key = serializers.CharField(
        max_length=255, required=False)
    aws_region = serializers.CharField(max_length=50, required=False)
    ses_configuration_set = serializers.CharField(
        max_length=255, required=False)
    iam_role_arn = serializers.CharField(max_length=255, required=False)
    enable_tracking = serializers.BooleanField(required=False)

    def validate(self, attrs):
        provider = attrs.get('provider')
        if provider == 'gmail':
            if not attrs.get('username') or not attrs.get('password'):
                raise serializers.ValidationError(
                    "Username and password are required for 'gmail' provider.")
        else:
            raise serializers.ValidationError(
                "Currently not accepting any other provider.")

        return attrs

    def create(self, validated_data):
        provider = validated_data.get("provider")
        username = validated_data.get("username")
        password = validated_data.get("password")
        user = validated_data.pop('user')

        obj = SMTPConfiguration.objects.create(
            provider=provider, username=username, password=password, user=user)
        return obj

    def update(self, instance, validated_data):
        provider = validated_data.get("provider")
        username = validated_data.get("username")
        password = validated_data.get("password")
        instance.provider = provider
        instance.username = username
        instance.password = password
        instance.save(update_fields=["provider", "username", "password"])

        return instance


class SMTPConfigurationSerializerForView(serializers.ModelSerializer):
    class Meta:
        model = SMTPConfiguration
        fields = "__all__"


class EmailComposeSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    body = serializers.CharField()
    configurations = serializers.PrimaryKeyRelatedField(
        queryset=SMTPConfiguration.objects.all())
    attachments = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True)

    def create(self, validated_data):
        attachments = validated_data.pop('attachments', [])
        user = validated_data.pop('user')

        instance = EmailCompose.objects.create(**validated_data, user=user)

        for attachment in attachments:
            EmailAttachment.objects.create(
                email_compose=instance, file=attachment)

        return instance


class EmailSendSerializer(serializers.Serializer):
    schedule_date = serializers.DateTimeField(required=False)
    notes = serializers.CharField(max_length=500, required=False)
    email_compose = serializers.PrimaryKeyRelatedField(
        queryset=EmailCompose.objects.all())
    group = serializers.PrimaryKeyRelatedField(
        queryset=EmailGroup.objects.all(), required=False)
    single_email = serializers.PrimaryKeyRelatedField(
        queryset=SingleEmail.objects.all(), required=False)

    def validate(self, attrs):
        if not attrs.get('group') and not attrs.get('single_email'):
            raise serializers.ValidationError(
                "Either 'group' or 'single_email' must be provided.")

        if attrs.get('group') and attrs.get('single_email'):
            raise serializers.ValidationError(
                "Only one of 'group' or 'single_email' can be provided.")

        email_compose = attrs.get("email_compose")
        if not email_compose.configurations:
            raise serializers.ValidationError(
                "This email compose has no email_configuration")

        if not email_compose.configurations.provider == 'gmail':
            raise serializers.ValidationError(
                "This email compose configuration provider not gmail.Currently not accepting any other provider.")

        return attrs

    def create(self, validated_data):
        objects = EmailSendRecord.objects.create(**validated_data)
        return objects


class EmailGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500, required=False)
    
    def validate_name(self, value):
        value = value.strip().lower()
        # Replace multiple spaces with a single underscore
        name = re.sub(r'\s+', '_', value)
        # Exclude current instance if it exists
        queryset = EmailGroup.objects.filter(name=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                f"Email group with name '{name}' already exists.")

        return name


    def create(self, validated_data):
        user = self.context.get("user")
        obj = EmailGroup.objects.create(**validated_data, user=user)
        return obj

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.user = validated_data.get('user', instance.user)
        instance.save(update_fields=['name', 'description', 'user'])
        return instance
        
class EmailListDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailList
        fields = ['id', 'email', 'is_subscribed']


class EmailGroupViewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EmailGroup
        fields = ['id', 'name', 'description', 'created_at',
                  'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailGroupSingleViewSerializer(serializers.ModelSerializer):
    email_lists = EmailListDetailsSerializer(
        many=True, read_only=True, source='group_email_lists')
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EmailGroup
        fields = ['id', 'name', 'description', 'created_at',
                  'updated_at', 'email_lists', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailListSerializer(serializers.Serializer):
    email = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False
    )
    is_subscribed = serializers.BooleanField(default=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=EmailGroup.objects.all())

    def validate(self, attrs):
        """
        Remove duplicates from input list, case-insensitive,
        and exclude (email, group) pairs that already exist in the database.
        """
        raw_emails = attrs.get('email', [])
        group = attrs.get('group')
        # Normalize emails
        normalized_emails = {email.strip().lower() for email in raw_emails}
        # Filter only those (email, group) that already exist
        existing_pairs = set(
            EmailList.objects.filter(
                email__in=normalized_emails,
                group=group
            ).values_list('email', flat=True)
        )
        # Remove those
        filtered_emails = list(normalized_emails - existing_pairs)

        if not filtered_emails:
            raise serializers.ValidationError("All emails already exist in this group.")

        attrs['email'] = filtered_emails
        return attrs

    def create(self, validated_data):
        emails = validated_data.pop('email')
        group = validated_data.get('group', None)
        is_subscribed = validated_data.get('is_subscribed', True)

        email_objs = [
            EmailList(email=email, is_subscribed=is_subscribed, group=group)
            for email in emails
        ]
        objs = EmailList.objects.bulk_create(email_objs)
        return objs


class EmailListSingleSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_subscribed = serializers.BooleanField()
    group = serializers.PrimaryKeyRelatedField(
        queryset=EmailGroup.objects.all())

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.is_subscribed = validated_data.get(
            'is_subscribed', instance.is_subscribed)
        instance.group = validated_data.get('group', instance.group)
        instance.save(update_fields=['email', 'is_subscribed', 'group'])
        return instance


class EmailGroupDetailsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EmailGroup
        fields = ['id', 'name', 'description',
                  'created_at', 'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailListViewSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EmailList
        fields = ['id', 'email', 'is_subscribed', 'group']
        read_only_fields = ['id']


class EmailListSingleViewSerializer(serializers.ModelSerializer):
    group = EmailGroupDetailsSerializer(read_only=True)

    class Meta:
        model = EmailList
        fields = ['id', 'email', 'is_subscribed', 'group']
        read_only_fields = ['id']


class SingleEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.strip().lower()
        queryset = SingleEmail.objects.filter(email=email)
        if self.instance:
            # Exclude current instance if it exists
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(f" {email} Email already exists")
        return email

    def create(self, validated_data):
        email = validated_data.get('email')
        obj = SingleEmail.objects.create(email=email)
        return obj

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class SingleEmailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleEmail
        fields = ['id', 'email']
        read_only_fields = ['id']


class EmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAttachment
        fields = ['file']


class EmailComposeViewSerializer(serializers.ModelSerializer):
    attachments = EmailAttachmentSerializer(
        source='emailattachment_set', many=True, read_only=True)

    class Meta:
        model = EmailCompose
        fields = ['id', 'subject', 'body', 'configurations', 'attachments']


class EmailComposeUpdateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255, required=False)
    body = serializers.CharField(required=False)
    configurations = serializers.PrimaryKeyRelatedField(
        queryset=SMTPConfiguration.objects.all(), required=False)
    attachments = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True)

    def update(self, instance, validated_data):
        if 'subject' in validated_data:
            instance.subject = validated_data['subject']

        if 'body' in validated_data:
            instance.body = validated_data['body']

        if 'configurations' in validated_data:
            instance.configurations = validated_data['configurations']

        attachments = validated_data.get('attachments')
        if attachments:
            instance.emailattachment_set.all().delete()
            for file in attachments:
                EmailAttachment.objects.create(
                    email_compose=instance, file=file)

        instance.save()
        return instance


class OutboxViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outbox
        fields = ['id', 'email_address', 'status', 'failed_reason',
                  'email_compose', 'created_at', 'updated_at', "is_from_template"]
        read_only_fields = ['id', 'created_at',
                            'updated_at', "is_from_template"]
