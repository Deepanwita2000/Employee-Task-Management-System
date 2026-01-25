import re
from rest_framework import serializers
from .models import Team

# 1. User Serializer
class TeamSerializer(serializers.ModelSerializer):
    project=serializers.StringRelatedField(read_only=True)
    manager=serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'project','manager','start_date','end_date' ]
        



    