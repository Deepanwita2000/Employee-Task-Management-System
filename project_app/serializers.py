from rest_framework import serializers
from .models import Project

class ProjecrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields=['id','title','description','project_file','created_at','updated_at']

  