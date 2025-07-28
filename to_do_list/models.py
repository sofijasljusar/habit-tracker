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
