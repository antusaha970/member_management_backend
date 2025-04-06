
from rest_framework import serializers
from .models import Venue
from .models import COUNTRY_CHOICES,Event,EVENT_STATUS_CHOICES
from member.models import Member

class EventVenueSerializer(serializers.Serializer):
    street_address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=255)
    state_province = serializers.CharField(max_length=255, required=False, default="")
    postal_code = serializers.CharField(max_length=20, required=False, default="")
    country = serializers.ChoiceField(choices=COUNTRY_CHOICES)

    def validate_street_address(self, value):
        """
        Ensure street address is not too short.
        """
        if len(value) < 5:
            raise serializers.ValidationError({"street_address":["Street address must be at least 5 characters"]})
        return value

    def validate_city(self, value):
        """
        Ensure city is not too short.
        """
        if len(value) < 3:
            raise serializers.ValidationError({"city": ["City name is too short."]})
        return value

    def validate_postal_code(self, value):
        """
        Ensure postal code is valid if provided.
        """
        if value and len(value) < 5:
            raise serializers.ValidationError({"postal_code": ["Postal code must be at least 4 characters."]})
        return value

    def validate(self, data):
        """
        Cross-field validation (e.g., postal code validation).
        """
        # Example: Check if postal code and state are required together.
        if data.get("state_province") and not data.get("postal_code"):
            raise serializers.ValidationError({"postal_code": ["Postal code is required when state/province is provided."]})
    
        return data
    
    def create(self, validated_data):
        """
        Create a new Venue instance.
        """
        venue = Venue.objects.create(**validated_data)
        return venue
        
class EventVenueViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"

class EventSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=EVENT_STATUS_CHOICES)
    registration_deadline = serializers.DateTimeField()
    event_type = serializers.CharField(max_length=255)
    reminder_time = serializers.DateTimeField()
    venue_id = serializers.PrimaryKeyRelatedField(queryset=Venue.objects.all(), required=False)
    organizer_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), required=False)

    def validate_title(self, value):
        
        if Event.objects.filter(title=value).exists():
            raise serializers.ValidationError({"title": ["An event with this title already exists."]})
        return value

    def create(self, validated_data):
        venue = validated_data.pop('venue_id', None)
        organizer = validated_data.pop('organizer_id', None)
        event = Event.objects.create(venue=venue, organizer=organizer, **validated_data)
        return event
