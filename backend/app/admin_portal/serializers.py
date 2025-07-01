from rest_framework import serializers
from .models import EducationInteraction, ActionInteraction


class EducationInteractionSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = EducationInteraction
        fields = ['id', 'userId', 'educationId', 'educationName', 'related_sdgs',
                  'related_disciplines', 'related_industries', 'timestamp']

    def get_timestamp(self, obj):
        return obj.timestamp.strftime('%d %b %Y, %I:%M:%S %p')


class ActionInteractionSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = ActionInteraction
        fields = ['id', 'userId', 'actionId', 'actionName',
                  'related_sdgs', 'related_industries', 'timestamp']

    def get_timestamp(self, obj):
        return obj.timestamp.strftime('%d %b %Y, %I:%M:%S %p')
