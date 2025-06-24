from rest_framework import serializers
from .models import *
from collections import Counter


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

        instance = Email_Compose.objects.create(**validated_data, user=user)

        for attachment in attachments:
            EmailAttachment.objects.create(
                email_compose=instance, file=attachment)

        return instance
    

class EmailGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500, required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_name(self, value):
        name = value.strip().lower().replace(" ", "_")
        # Exclude current instance if it exists
        queryset = EmailGroup.objects.filter(name=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                f"Email group with name '{name}' already exists.")

        return name

    def create(self, validated_data):
        obj = EmailGroup.objects.create(**validated_data)
        return obj

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.user = validated_data.get('user', instance.user)
        instance.save(update_fields=['name', 'description', 'user'])
        return instance


class EmailGroupViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailGroup
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class EmailListSerializer(serializers.Serializer):
    email = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False
    )
    is_subscribed = serializers.BooleanField(default=True)
    group = serializers.PrimaryKeyRelatedField(queryset=EmailGroup.objects.all())

    def validate_email(self, value):
        """
        Remove duplicates from input email list (case-insensitive),
        and exclude emails that already exist in the database.
        """
        normalized_emails = {email.strip().lower() for email in value}

        if not normalized_emails:
            return []
        existing_emails = set(
            EmailList.objects.filter(email__in=normalized_emails)
            .values_list('email', flat=True)
        )
        return list(normalized_emails - existing_emails)
            
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
    group = serializers.PrimaryKeyRelatedField(queryset=EmailGroup.objects.all())

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.is_subscribed = validated_data.get(
            'is_subscribed', instance.is_subscribed)
        instance.group = validated_data.get('group', instance.group)
        instance.save(update_fields=['email', 'is_subscribed', 'group'])
        return instance
    
    
class EmailListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailList
        fields = ['id', 'email', 'is_subscribed', 'group']
        read_only_fields = ['id']

class SingleEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self,value):
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
        model = Email_Compose
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
