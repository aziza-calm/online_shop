from rest_framework import serializers
from .models import Courier


class CourierSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100)
    regions = serializers.ListSerializer(child=serializers.IntegerField())
    working_hours = serializers.ListSerializer(child=serializers.CharField(max_length=100))

    def create(self, validated_data):
        return Courier.objects.create(**validated_data)
