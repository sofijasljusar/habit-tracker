# ✅ Habit Tracker

## Overview
Backend-focused Django application for tracking personal habits and daily tasks.

The application is built around date-driven workflows (daily and monthly views), allowing users to manage tasks, track habits, and review history over time.

## Key Features
- Daily task management
- Habit tracking with per-day records
- Progress history

## Architecture & Design
Built with Django, using Django REST Framework (DRF) to expose selected functionality via API endpoints.

### Domain Modeling
The core domain is centered around time-based user behavior:
- `Habit` — habit definition
- `HabitRecord` — completion on a specific date
- `HabitTrackingMonth` — controls which habits are active in a given month

This separation allows flexible tracking, reuse of habits across months, and efficient querying for calendar and history views.

### Backend Logic
- Non-trivial date handling (multiple day views, calendar generation)
- Formsets for managing multiple related objects
- User-scoped data access across all views
- Formsets for managing multiple related objects in a single request

### Data Access & Performance
- Query optimization using `prefetch_related`
- Filtered prefetching for month-specific data
- Aggregations using `TruncMonth` and `Count` for history views

## What I Focused On
- Implementing non-trivial backend logic around dates and tracking
- Writing efficient ORM queries for real-world use cases
- Building a complete, user-facing backend-driven application

## Installation & Run
Create new folder and open in IDE, in terminal run:
```
git clone https://github.com/sofijasljusar/habit-tracker.git
python3 -m venv .venv
source .venv/bin/activate
cd habit-tracker               
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
