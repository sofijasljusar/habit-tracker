# ✅ Habit Tracker

## Overview
A full-stack application (backend-focused) for tracking habits and generating time-based progress insights.

The system is built around the natural time structures users rely on (days, weeks, months), making it intuitive to track consistency and long-term progress.

## Key Features
- Time-based tracking and aggregation
- JWT-based authentication
- Monthly analytics and progress insights

## Architecture & Design
Built with Django and PostgreSQL, with emphasis on clean architecture, modularity, and separation of concerns.

The system models time explicitly as a core part of the domain, enabling efficient aggregation and meaningful analytics.

Key design considerations:
- Domain-driven modeling around time-based behavior
- Efficient aggregation queries for analytics
- Authentication and user isolation

## Tech Stack
- Django
- PostgreSQL
- JWT authentication

## What I Focused On
- Designing a domain model centered around time-based user behavior
- Building modular and maintainable backend architecture
- Implementing efficient aggregation logic for analytics

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
