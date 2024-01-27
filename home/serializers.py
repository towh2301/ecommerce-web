from rest_framework import serializers
from .models import *


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'date_of_birth')


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='userprofile')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_profile')


class LineItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = LineItem
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    items = LineItemSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Payment
        fields = '__all__'


class OrderSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_spent = serializers.IntegerField()


