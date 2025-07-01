from rest_framework import serializers
from .models import ActionDb


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionDb
        fields = '__all__'
