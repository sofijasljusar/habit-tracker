from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    HomeView,
    SignUpView,
    LogInView,
    HistoryMenuView,
    AboutView,
    HabitCreateView,
    ToDoHistoryView,
    ToDoHistoryDetailView,
    HabitMonthHistoryView,
    HabitMonthHistoryDetailView,
    SettingsView,
    TrackHabitsView,
    UntrackHabitsView,
)
from .api_views import (
    HabitRecordToggleView,
    AvailableHabitsAPIView,
    TrackedHabitsAPIView,
    UpdateThemeColorView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LogInView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/theme/', UpdateThemeColorView.as_view(), name="theme-update"),
    path('about/', AboutView.as_view(), name='about'),
    path('habits/add/', HabitCreateView.as_view(), name='habit-add'),
    path('api/habits/toggle/', HabitRecordToggleView.as_view(), name='habit-toggle'),
    path('api/habits/available/', AvailableHabitsAPIView.as_view(), name='habits-available'),
    path('habits/track/', TrackHabitsView.as_view(), name='habits-track'),
    path('api/habits/tracked/', TrackedHabitsAPIView.as_view(), name='habits-tracked'),
    path('habits/untrack/', UntrackHabitsView.as_view(), name='habits-untrack'),
    path('history/', HistoryMenuView.as_view(), name='history-menu'),
    path('history/todo/', ToDoHistoryView.as_view(), name="todo-history"),
    path('history/todo/<slug:date>/', ToDoHistoryDetailView.as_view(), name="todo-history-detail"),
    path('history/habits/', HabitMonthHistoryView.as_view(), name="habit-history"),
    path('history/habits/<slug:month>/', HabitMonthHistoryDetailView.as_view(), name="habit-history-detail"),
]
