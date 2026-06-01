from django.urls import path
from .views import (HomeView,
                    SignUpView,
                    LogInView,
                    HistoryMenuView,
                    AboutView,
                    HabitCreateView,
                    HabitRecordToggleView,
                    ToDoHistoryView,
                    ToDoHistoryDetailView,
                    HabitMonthHistoryView,
                    HabitMonthHistoryDetailView,
                    SettingsView,
                    UpdateThemeColorView,
                    OldHabitsModalView,
                    UntrackHabitsModalView)
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('add-habit/', HabitCreateView.as_view(), name='add-habit'),
    path('toggle-habit/<int:habit_id>/<int:year>/<int:month>/<int:day>/',
         HabitRecordToggleView.as_view(), name='toggle-habit'),
    path('old-habits/', OldHabitsModalView.as_view(), name='old-habits'),
    path('untrack-habits/', UntrackHabitsModalView.as_view(), name='untrack-habits'),
    path('history/', HistoryMenuView.as_view(), name='history-menu'),
    path('todo-history/', ToDoHistoryView.as_view(), name="todo-history"),
    path('todo-history/<slug:date>/', ToDoHistoryDetailView.as_view(), name="todo-history-detail"),
    path('habit-history/', HabitMonthHistoryView.as_view(), name="habit-history"),
    path('habit-history/<slug:month>/', HabitMonthHistoryDetailView.as_view(), name="habit-history-detail"),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('update-theme-color/', UpdateThemeColorView.as_view(), name="update-theme-color"),
    path('about/', AboutView.as_view(), name='about'),
]
