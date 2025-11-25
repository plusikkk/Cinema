from django.contrib.auth import get_user_model
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
        extra_kwargs = {'username': {'required': True, 'max_length': 20},
                        'password': {'write_only': True, 'min_length': 8, 'max_length': 50},}

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

    def validate_username(self, value):
       User = get_user_model()
       if not self.instance and User.objects.filter(username=value).exists():
          raise serializers.ValidationError('Це ім`я вже зайняте')
       if self.instance and self.instance.username == value:
       if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Це ім`я вже зайняте')
       return value


    def update(self, instance, validated_data):
      password = validated_data.get('password', None)
      user = super().update(instance, validated_data)

      if password:
        user.set_password(password)
        user.save()

      return user

