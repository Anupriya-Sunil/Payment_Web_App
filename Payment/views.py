from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import WalletDb, TransactionDb
from .serializers import RegisterSerializer, WalletSerializer, TransactionSerializer
from decimal import Decimal
import uuid


# REGISTER
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Registration successful"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# WALLET
@api_view(['GET'])
def wallet(request):
    user_id = request.query_params.get('user_id')

    try:
        wallet = WalletDb.objects.get(user_id=user_id)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    except WalletDb.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=404)


# ADD MONEY
@api_view(['POST'])
def add_money(request):
    user_id = request.data.get('user_id')
    amount = Decimal(str(request.data.get('amount', 0)))

    try:
        wallet = WalletDb.objects.get(user_id=user_id)

        if amount <= 0:
            return Response({"error": "Invalid amount"}, status=400)

        wallet.balance += amount
        wallet.save()

        return Response({"message": "Money added successfully",
                         "balance": wallet.balance})

    except WalletDb.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=404)


# SEND MONEY
@api_view(['POST'])
def send_money(request):
    sender_id = request.data.get('sender_id')
    receiver_id = request.data.get('receiver_id')
    amount = Decimal(str(request.data.get('amount', 0)))

    if amount <= 0:
        return Response({"error": "Invalid amount"}, status=400)

    try:
        sender_wallet = WalletDb.objects.get(user_id=sender_id)
        receiver_wallet = WalletDb.objects.get(user_id=receiver_id)

        if sender_id == receiver_id:
            return Response({"error": "Cannot send money to yourself"}, status=400)

        if sender_wallet.balance < amount:
            return Response({"error": "Insufficient balance"}, status=400)

        sender_wallet.balance -= amount
        receiver_wallet.balance += amount

        sender_wallet.save()
        receiver_wallet.save()

        transaction = TransactionDb.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            transaction_id=str(uuid.uuid4())
        )

        return Response({
            "message": "Payment successful",
            "transaction_id": transaction.transaction_id
        })

    except WalletDb.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=404)


# TRANSACTION HISTORY
@api_view(['GET'])
def transactions(request):
    user_id = request.query_params.get('user_id')

    data = TransactionDb.objects.filter(
        sender_id=user_id
    ) | TransactionDb.objects.filter(receiver_id=user_id)

    serializer = TransactionSerializer(data, many=True)
    return Response(serializer.data)