from django.shortcuts import render
from rest_framework import generics
from .models import Fund
from .serializers import FundSerializer

class FundListAPIView(generics.ListAPIView):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
