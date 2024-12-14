import os
from carrer.models import Carrers
from rest_framework import serializers

class CarrerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrers
        fields = '__all__'

class CarrerFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate(self, data):
        if data['file'].name.split('.')[-1] not in ['xlsx', 'csv']:
            raise serializers.ValidationError("O arquivo precisa ser um xlsx")
        
        return data

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=50)