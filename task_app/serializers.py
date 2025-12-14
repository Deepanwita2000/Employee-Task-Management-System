from rest_framework import serializers
from .models import Task
from account_app.models import User
class TaskSerializer(serializers.ModelSerializer):
    employee_email = serializers.CharField(write_only=True)  
    assigned_to = serializers.StringRelatedField(read_only=True)  # Display employee_name in response
    assigned_to_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = Task
        fields ='__all__'
        extra_kwargs = {                
            'assigned_by': {'read_only': True}            # DRF will not include the password in any GET response.
        }
    def validate_description(self, value):
        # Check if name is only digits
        if len(value)>=500:
            raise serializers.ValidationError("characters should not exeed more than 500.")


        return value

    def create(self, validated_data):
        print(validated_data)
        employee_email = validated_data.pop('employee_email')
        

        try:
            # So whatever employee_email I gave in POST based on that it will search the  ID
            employee = User.objects.get(email=employee_email)   
            print((employee.email))  
        except User.DoesNotExist:
            raise serializers.ValidationError({'employee': 'employee not found.'})
        task = Task.objects.create(assigned_to=employee, **validated_data)
        print(task)
        return task
