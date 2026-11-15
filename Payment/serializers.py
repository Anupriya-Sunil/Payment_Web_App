from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WalletDb, TransactionDb


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        WalletDb.objects.create(user=user)
        return user


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletDb
        fields = '__all__'
        
class TransactionSerializer(serializers.ModelSerializer):

    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = TransactionDb
        fields = [
            'id',
            'sender_name',
            'receiver_name',
            'amount',
            'transaction_id',
            'date'
        ]
