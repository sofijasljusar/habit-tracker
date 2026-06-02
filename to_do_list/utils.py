import calendar
from datetime import date


def build_month_calendar(year, month):
    cal = calendar.Calendar(firstweekday=0) # Returns a matrix: each inner list represents a week (Mon = 0)

    return [
        [date(year, month, day) if day else None for day in week]
        for week in cal.monthdayscalendar(year, month)
    ]
