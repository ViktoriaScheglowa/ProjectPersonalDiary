from rest_framework import serializers

from goal.models import Goal
from goal.validators import (
    CheckGoalValidator,
    DateDeadlineGoalValidator,
    )


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = "__all__"
        validators = [
            CheckGoalValidator(
                is_active="is_active",
                is_public="is_public",
            ),
            DateDeadlineGoalValidator(date_deadline="date_deadline"),
            ]
        extra_kwargs = {"owner": {"read_only": True}}


class PublicListGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ("id", "title", "action", "is_progress", "time_deadline", "is_public")
