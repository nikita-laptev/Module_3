from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mission, SpaceFlight, Booking

User = get_user_model()

# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'birth_date')

# Сериализатор для регистрации пользователей
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'birth_date')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Сериализатор для космических миссий
class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = '__all__'

# Сериализатор для космических полетов
class SpaceFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceFlight
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
