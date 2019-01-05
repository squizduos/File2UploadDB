from rest_framework import serializers

from .models import User


class UserLoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})


class UserCreateRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, max_length=255)

    class Meta:
        model = User
        fields = ['username', 'email']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSetPasswordRequestSerializer(serializers.Serializer):
    model = User

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if 'login_hash' not in data:
            raise serializers.ValidationError("Can't find user without login_hash")
        if not self.model.objects.filter(login_hash=data['login_hash']):
            raise serializers.ValidationError("User with login hash does not exist")
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords are not match")
        return data
    
    login_hash = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, min_length=8, required=True)
    confirm_password = serializers.CharField(max_length=128, min_length=8, required=True)


class UserRegisterResponseSerializer(serializers.Serializer):
    registered = serializers.BooleanField()
