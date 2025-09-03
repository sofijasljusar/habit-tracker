from django.contrib import admin

from .models import HabitTrackingMonth, UserProfile


@admin.register(HabitTrackingMonth)
class HabitTrackingMonthAdmin(admin.ModelAdmin):
    list_display = ("habit", "year", "month")
    list_filter = ("habit", "year", "month")


admin.site.register(UserProfile)
