from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator


class UserSerializer(serializers.ModelSerializer):
    password_check = serializers.CharField(write_only=True, max_length=50)
    password = serializers.CharField(write_only=True, validators=[validate_password], max_length=50)
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_check']
        extra_kwargs = {'username': {'required': True, 'max_length': 50}}

    def validate(self, data):
        if 'password' in data and 'password_check' in data:
            if data['password'] != data['password_check']:
                raise serializers.ValidationError('Passwords must match')
        return data

    def create(self, validated_data):
        validated_data.pop('password_check', None)
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        User = get_user_model()
        if self.instance and self.instance.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Це ім`я вже зайняте')
        return value

    def validate_email(self, value):
        User = get_user_model()
        if self.instance and self.instance.email == value:
            return value

        user_exists = User.objects.filter(email__iexact=value).first()

        if user_exists:
            if not user_exists.is_active:
                raise serializers.ValidationError('Ця електронна адреса вже зайнята')
        return value

    def update(self, instance, validated_data):
        validated_data.pop('password_check', None)
        password = validated_data.get('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

