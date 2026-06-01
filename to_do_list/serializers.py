from rest_framework import serializers


class ToggleHabitRecordSerializer(serializers.Serializer):
    habit_id = serializers.IntegerField()
    date = serializers.DateField()
