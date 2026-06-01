from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .serializers import ToggleHabitRecordSerializer
from .models import Habit, HabitRecord

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

