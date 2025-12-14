import re
from rest_framework import serializers

from account_app.models import User
from task_app.models import Task
from .models import Comment




class CommentSerializer(serializers.ModelSerializer):
      

    class Meta:
        model = Comment
        fields='__all__'
        extra_kwargs = {                
            'task': {'read_only': True}   ,
            'commented_by' : {'read_only': True}                
        }

    def validate_comment_text(self, value):
        # Check if name is only digits
        if len(value)>=200:
            raise serializers.ValidationError("characters should not exeed more than 500.")

        
        return value

        