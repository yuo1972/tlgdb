from rest_framework import serializers
from .models import Tlg


class TlgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tlg
        fields = "__all__"
