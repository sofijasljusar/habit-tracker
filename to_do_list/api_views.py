from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone

from .serializers import ToggleHabitRecordSerializer, HabitSerializer
from .models import Habit, HabitRecord, HabitTrackingMonth


def get_tracked_habit_ids(user):
    today = timezone.localdate()
    return HabitTrackingMonth.objects.filter(
        habit__user=user,
        year=today.year,
        month=today.month,
    ).values_list("habit_id", flat=True)



class HabitRecordToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ToggleHabitRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        habit_id = serializer.validated_data["habit_id"]
        date = serializer.validated_data["date"]

        habit = get_object_or_404(Habit, id=habit_id, user=request.user)

        record, created = HabitRecord.objects.get_or_create(
            habit=habit,
            date=date
        )

        if not created:
            record.delete()
            return Response({"status": "deleted"})
        return Response({"status": "created"})


class AvailableHabitsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_habits = Habit.objects.filter(user=request.user)
        tracked_this_month = get_tracked_habit_ids(user=request.user)
        habits_to_track = user_habits.exclude(id__in=tracked_this_month)

        serializer = HabitSerializer(habits_to_track, many=True)
        return Response({"habits": serializer.data})


class TrackedHabitsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_habits = Habit.objects.filter(user=request.user)
        tracked_this_month = get_tracked_habit_ids(user=request.user)
        habits_to_untrack = user_habits.filter(id__in=tracked_this_month)

        serializer = HabitSerializer(habits_to_untrack, many=True)
        return Response({"habits": serializer.data})
