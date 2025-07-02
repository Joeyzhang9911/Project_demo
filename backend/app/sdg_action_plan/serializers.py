from rest_framework import serializers
from .models import SDGActionPlan


class SDGActionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDGActionPlan
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # Remove the team field if it's present to prevent updating it
        validated_data.pop('team', None)
        return super().update(instance, validated_data)
