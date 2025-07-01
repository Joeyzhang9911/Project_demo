from rest_framework import serializers
from .models import EducationDb


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDb
        fields = '__all__'
