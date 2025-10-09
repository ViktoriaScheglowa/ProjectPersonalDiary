from rest_framework import serializers

from moments.models import Moment
from moments.validators import ValidateCreate


class MomentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moment
        fields = "__all__"
        validators = [
            ValidateCreate(created_at="created_at"),
        ]
        extra_kwargs = {"owner": {"read_only": True}}


class PublicListMomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moment
        fields = ("id", "title", "location", "created_at", "is_public")
