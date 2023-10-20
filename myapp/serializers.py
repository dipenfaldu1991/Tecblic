from rest_framework import serializers
from .models import UserProfile

from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True,write_only=True)
    first_name = serializers.CharField(max_length=100,required=True,allow_blank=False, allow_null=False)
    middle_name = serializers.CharField(max_length=100,required=True,allow_blank=True, allow_null=True)
    last_name = serializers.CharField(max_length=100,required=True,allow_blank=False, allow_null=False)
    last_name = serializers.CharField(max_length=100,required=True,allow_blank=False, allow_null=False)
    role = serializers.EmailField(max_length=100,required=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email','role','first_name','middle_name','last_name')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    class Meta:
        fields = ('old_password','new_password','confirm_password')


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    class Meta:
        fields = ('email')

class UserProfileSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False,allow_null=True)
    phone_number = serializers.CharField(required=False,allow_null=True)
    avatar = serializers.ImageField(required=False,allow_null=True)
    # user = serializers.PrimaryKeyRelatedField(required=True,queryset=User.objects.filter(is_active=True),error_messages={
    #         'does_not_exist': 'The requested User does not exist.',
    #         'incorrect_type': 'Incorrect type. Expected pk value, received {data_type}.'
    #     })
    class Meta:
        model = UserProfile
        fields = ('id','bio', 'avatar','phone_number',)  # Include all fields you want to expose