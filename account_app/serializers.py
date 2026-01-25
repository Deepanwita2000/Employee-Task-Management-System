import re
from rest_framework import serializers
from .models import User

# 1. User Serializer
# class UserSerializer(serializers.ModelSerializer):
    # password_confirm = serializers.CharField(write_only=True)

    # class Meta:
    #     model = User
    #     fields = ['id', 'email','bio' ,'username','gender', 'first_name', 'last_name','role'
    #          , 'password', 'password_confirm','designation','date_joined','yop','age','image'

    #              ]
    #     extra_kwargs = {                
    #         'password': {'write_only': True}   ,         # DRF will not include the password in any GET response.
    #         'role': {'required': False}            # role will be either manager or employee
    #     }

    # Custom validation for email ending with a specific domain
    # def validate_email(self, value):
    #     if not value.endswith('@gmail.com'):
    #         raise serializers.ValidationError("Only '@gmail.com' emails are allowed.")
    #     return value

    # def validate_username(self, value):
    #     if len(value) < 4:
    #         raise serializers.ValidationError("Username must be at least 4 characters long.")
    #     return value
    
    # def validate_role(self, value):
    #     if value not in ('manager' , 'role'):
    #         raise serializers.ValidationError("Invalid role.")
    #     return value

    # def validate_password(self, value):
    #     if len(value) < 8:
    #         raise serializers.ValidationError("Password must be at least 8 characters long.")
    #     if not re.search(r'[A-Z]', value):
    #         raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    #     if not re.search(r'[0-9]', value):
    #         raise serializers.ValidationError("Password must contain at least one digit.")
    #     return value
  
    # def validate(self, data):  # data containes the dictionary -> all the vales are stored as dictionary
    #     print("validate : ", data)
    #     print("validate role : ", data['role'])
    #     if data['role'] == 'manager' and data['designation'] not in {'IT Manager' , 'Assisstant Manager' , 'Sr.Manager'}:
    #         raise serializers.ValidationError("Invalid designation !!. Must be in these {'IT Manager' , 'Assisstant Manager' , 'Sr.Manager'}")

        
    #     if data.get('password') != data.get('password_confirm'):
    #         raise serializers.ValidationError("Passwords do not match.")
    #     if data['first_name'].lower() == data['last_name'].lower():
    #         raise serializers.ValidationError("First name and last name cannot be the same.")
    #     return data

    # def create(self, validated_data):
    #     validated_data.pop('password_confirm')                  # password_confirm is not a field in the model
    #     password = validated_data.pop('password')               # We cannot save password directly, it needs to be hashed
    #     role = validated_data.pop('role', None)  # <--- NEW

    #     user = User(**validated_data)

    #     if role:
    #         user.role = role  # <--- SAVE ROLE
    #     print("inside create: ", validated_data)
    #     user = User(**validated_data)                           # Create a new User instance
    #     user.set_password(password)                             # Hash the password        
    #     user.save()                                             # Save the user instance     
    # #     return user

    # def create(self, validated_data):
    #     validated_data.pop('password_confirm')
    #     password = validated_data.pop('password')

    #     role = validated_data.pop('role', None)

    #     user = User(**validated_data)

    #     if role:
    #         user.role = role

    #     user.set_password(password)
    #     user.save()
    #     return user
    
class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    # is_approved = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=False)
    role = serializers.CharField(read_only=True)
    # image=serializers.ImageField(max_length=None , use_url=True , required=False)
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'password', 'password_confirm','is_active','bio','designation_e','designation_m','gender','date_joined','yop','age','image']
        extra_kwargs = {                
            'password': {'write_only': True}   ,         # DRF will not include the password in any GET response.
            "designation_m": {"required": False, "allow_null": True},
            "designation_e": {"required": False, "allow_null": True},

        }

    # Custom validation for email ending with a specific domain
    def validate_email(self, value):
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError("Only '@gmail.com' emails are allowed.")
        return value

    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Username must be at least 4 characters long.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        return value
  
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")
        if data['first_name'].lower() == data['last_name'].lower():
            raise serializers.ValidationError("First name and last name cannot be the same.")
        
        role = data.get("role")
        if role == User.EMPLOYEE:
            if not data.get("designation_e"):
                raise serializers.ValidationError(
                     {"designation_e": "Employee designation is required"}
                )
            data['designation_m']=None
        elif role == User.MANAGER:
            if not data.get("designation_m"):
                raise serializers.ValidationError(
                        {"designation_m": "manager designation is required"}
                )
            data['designation_e']=None
        
        return data



#  extra_kwargs = {
#             "password": {"write_only": True},
#             "designation_m": {"required": False, "allow_null": True},
#             "designation_e": {"required": False, "allow_null": True},
#         }

#     def validate(self, attrs):
#         role = attrs.get("role")

#         if role == User.EMPLOYEE:
#             if not attrs.get("designation_e"):
#                 raise serializers.ValidationError(
#                     {"designation_e": "Employee designation is required"}
#                 )
#             attrs["designation_m"] = None

#         elif role == User.MANAGER:
#             if not attrs.get("designation_m"):
#                 raise serializers.ValidationError(
#                     {"designation_m": "Manager designation is required"}
#                 )
#             attrs["designation_e"] = None

#         return attrs





    def create(self, validated_data):
        validated_data.pop('password_confirm')                  # password_confirm is not a field in the model
        password = validated_data.pop('password')               # We cannot save password directly, it needs to be hashed
        user = User(**validated_data)                           # Create a new User instance
        user.set_password(password)                             # Hash the password        
        user.save()                                             # Save the user instance     
        return user

