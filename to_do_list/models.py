from django.db import models
from django.contrib.auth.models import User


class ToDoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todo_lists")
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class ToDoItem(models.Model):
    to_do_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'✓' if self.completed else '✗'})"


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class HabitRecord(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="records")
    date = models.DateField()

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['date']


class HabitTrackingMonth(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="months_tracked")
    year = models.IntegerField()
    month = models.IntegerField()

    class Meta:
        unique_together = ("habit", "year", "month")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme_color = models.CharField(max_length=7, default="27DDF5")

    def __str__(self):
        return f"{self.user.username.capitalize()} Profile"
