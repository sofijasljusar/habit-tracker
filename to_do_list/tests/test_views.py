import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from to_do_list.models import Habit, HabitTrackingMonth
from freezegun import freeze_time

@pytest.mark.django_db
def test_tracking_habit_adds_month_entry(client):
    user = User.objects.create_user(username="u1", password="pass")
    habit = Habit.objects.create(user=user, name="Run")

    client.force_login(user)

    url = reverse("habits-track")
    client.post(url, {"habits": [habit.id]})

    assert HabitTrackingMonth.objects.filter(habit=habit).exists()


@freeze_time("2026-01-01")
@pytest.mark.django_db
def test_untracking_removes_month_entry(client):
    user = User.objects.create_user(username="u1", password="pass")
    habit = Habit.objects.create(user=user, name="Run")

    HabitTrackingMonth.objects.create(habit=habit, year=2026, month=1)

    client.force_login(user)

    url = reverse("habits-untrack")
    client.post(url, {"habits": [habit.id]})

    assert not HabitTrackingMonth.objects.filter(habit=habit).exists()


@pytest.mark.django_db
def test_home_view_authenticated_returns_200(client):
    user = User.objects.create_user(username="u1", password="pass")
    client.force_login(user)

    response = client.get(reverse("home"))

    assert response.status_code == 200


def test_home_view_anonymous_shows_welcome(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert "welcome.html" in [t.name for t in response.templates]