from django.test import TestCase
import datetime

# Create your tests here.
if __name__ == '__main__':
    today = datetime.datetime.today()
    first_day_of_week = today - datetime.timedelta(days=today.weekday())
    last_day_of_week = today + datetime.timedelta(days=7 - today.weekday())
    print first_day_of_week
    print last_day_of_week

    y = today.year
    m = today.month
    month_start_dt = datetime.date(y, m, 1)
    print month_start_dt

    if m == 12:
        month_end_dt = datetime.date(y + 1, 1, 1) - datetime.timedelta(days=1)
        print month_end_dt

    else:
        month_end_dt = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
        print month_end_dt

    _min = today + datetime.timedelta(hours=2.5)
    print float((_min - today).seconds)/3600