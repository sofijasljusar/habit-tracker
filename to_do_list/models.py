from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class ToDoList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="todo_lists")
    date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"],
                name="unique_todo_list_per_day"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class ToDoItem(models.Model):
    to_do_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'✓' if self.completed else '✗'})"


class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class HabitRecord(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="records")
    date = models.DateField()

    class Meta:
        ordering = ['date']

        constraints = [
            models.UniqueConstraint(
                fields=["habit", "date"],
                name="unique_habit_record_per_day"
            )
        ]

    def __str__(self):
        return f"{self.habit} - {self.date}"


class HabitTrackingMonth(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="months_tracked")
    year = models.IntegerField()
    month = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["habit", "year", "month"],
                name="unique_habit_per_month"
            )
        ]

    def __str__(self):
        return f"{self.habit} ({self.month}-{self.year})"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme_color = models.CharField(max_length=7, default="#27DDF5")

    def __str__(self):
        return f"{self.user.username.capitalize()} Profile"
