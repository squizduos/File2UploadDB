from rest_framework import serializers

from .models import User


class AdminRegistrationSerializer(serializers.ModelSerializer):
    """Creates new user and send him email."""
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['username', 'email', '']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    confirm_password = serializers.CharField(max_length=255)
    login_hash = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'login_hash']

    # def create(self, validated_data):
    #     return User.objects.create_user(**validated_data)

