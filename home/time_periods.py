import datetime


def bedtime():
    return datetime.datetime.combine(
        datetime.date.today(),
        datetime.time(11, 45)
    )

