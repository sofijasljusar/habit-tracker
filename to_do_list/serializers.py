from rest_framework import serializers

from .models import Habit


class ToggleHabitRecordSerializer(serializers.Serializer):
    habit_id = serializers.IntegerField()
    date = serializers.DateField()


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ("id", "name")
