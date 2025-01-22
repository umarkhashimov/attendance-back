from datetime import datetime, timedelta

def course_date_match(course) -> bool:
    now = datetime.now()

    course_weekdays = [x for x in course.weekdays]
    lesson_time = datetime.combine(datetime.today(), course.lesson_time)
    lesson_endtime = lesson_time + timedelta(minutes=course.duration)
    time_now = datetime.now().time().strftime("%H:%M")

    weekday_match = str(now.weekday()) in course_weekdays
    time_match = time_now >= lesson_time.strftime("%H:%M") and time_now <= lesson_endtime.strftime("%H:%M")

    print("check_time", weekday_match and time_match)

    return f'{now} | {time_now}: {time_match}'
    # return True

    
    
    
def early_to_conduct_session(session) -> bool:
    session_datetime = datetime.combine(session.date, session.course.lesson_time)
    time_now = datetime.now()

    if time_now < session_datetime:
        return True
    else:
        return False 