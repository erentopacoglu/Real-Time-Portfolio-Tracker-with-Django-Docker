from rest_framework import serializers
from .models import Fund

class FundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fund
        fields = '__all__' # Tüm alanları (id, code, quantity, buy_price, created_at) JSON'a dök