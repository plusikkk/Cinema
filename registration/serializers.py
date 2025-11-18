from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name','username', 'email', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5, 'max_length': 8},
                        "first_name": {"required": False, "allow_blank": True},
                        "last_name": {"required": False, "allow_blank": True},
                        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user




