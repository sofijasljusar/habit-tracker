from rest_framework import serializers

from .models import Habit


class ToggleHabitRecordSerializer(serializers.Serializer):
    habit_id = serializers.IntegerField()
    date = serializers.DateField()


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ("id", "name")


class ThemeColorSerializer(serializers.Serializer):
    theme_color = serializers.RegexField(
        regex=r"^#[0-9a-fA-F]{6}$"
    )
