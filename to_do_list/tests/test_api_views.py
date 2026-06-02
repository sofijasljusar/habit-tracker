import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from to_do_list.models import Habit, HabitRecord


@pytest.mark.django_db
def test_toggle_creates_habit_record(client):
    user = User.objects.create_user(username="u1", password="pass")
    habit = Habit.objects.create(user=user, name="Run")

    client.force_login(user)

    url = reverse("habit-toggle")
    response = client.post(url, {"habit_id": habit.id, "date": "2026-01-01"})

    assert response.status_code == 200
    assert HabitRecord.objects.filter(habit=habit).exists()


@pytest.mark.django_db
def test_toggle_deletes_habit_record(client):
    user = User.objects.create_user(username="u1", password="pass")
    habit = Habit.objects.create(user=user, name="Run")

    HabitRecord.objects.create(habit=habit, date="2026-01-01")

    client.force_login(user)

    url = reverse("habit-toggle")
    response = client.post(url, {"habit_id": habit.id, "date": "2026-01-01"})

    assert response.status_code == 200
    assert not HabitRecord.objects.filter(habit=habit).exists()


@pytest.mark.django_db
def test_toggle_rejects_other_users_habit(client):
    user1 = User.objects.create_user(username="u1", password="pass")
    user2 = User.objects.create_user(username="u2", password="pass")

    habit = Habit.objects.create(user=user1, name="Run")

    client.force_login(user2)

    url = reverse("habit-toggle")
    response = client.post(url, {"habit_id": habit.id, "date": "2026-01-01"})

    assert response.status_code == 404