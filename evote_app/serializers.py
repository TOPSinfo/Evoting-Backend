from rest_framework import serializers
from .models import *


class CandidateSserializer(serializers.ModelSerializer):
    # party_symbol = serializers.ImageField(required=False)

    class Meta:
        model = Candidates
        fields = (
            "id",
            "full_name",
            "party_name",
            "qualification",
            "age",
        )
