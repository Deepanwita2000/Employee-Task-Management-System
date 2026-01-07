import re
from rest_framework import serializers
from .models import Task2

# 1. User Serializer
class TaskSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Task2
        fields = ['id', 'tasks','domain','project','manager','end_date','created_at','updated_at' ]
        extra_kwargs = {                
            'manager': {'read_only': True}            
        }