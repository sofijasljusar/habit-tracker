from django.contrib import admin

from .models import UserProfile, Habit, HabitTrackingMonth, HabitRecord


admin.site.register(UserProfile)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name", "user__username")


@admin.register(HabitTrackingMonth)
class HabitTrackingMonthAdmin(admin.ModelAdmin):
    list_display = ("habit", "year", "month")
    list_filter = ("habit", "year", "month")
    search_fields = ("habit__name",)
    ordering = ("-year", "-month")


@admin.register(HabitRecord)
class HabitRecordAdmin(admin.ModelAdmin):
    list_display = ("habit", "date")
    list_filter = ("date",)
