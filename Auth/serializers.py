from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator


class UserSerializer(serializers.ModelSerializer):
    password_check = serializers.CharField(write_only=True, max_length=20)
    password = serializers.CharField(write_only=True, validators=[validate_password], max_length=20)
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_check']
        extra_kwargs = {'username': {'required': True, 'max_length': 20}}

    def validate(self, data):
        if data['password'] != data['password_check']:
            raise serializers.ValidationError('Passwords must match')
        return data

    def create(self, validated_data):
        validated_data.pop('password_check')
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


