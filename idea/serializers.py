from rest_framework import serializers

from idea.models import Myidea
from idea.validators import (
    OffensiveWordValidator,
    ConditionalLengthValidator,
)


class IdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Myidea
        fields = "__all__"
        validators = [
            OffensiveWordValidator(
                comments="comments",
            ),
            ConditionalLengthValidator(
                comments="comments",
            ),
        ]
        extra_kwargs = {"owner": {"read_only": True}}


class PublicListIdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Myidea
        fields = ("id", "title", "comments", "is_public")
