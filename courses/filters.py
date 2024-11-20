from datetime import datetime, timedelta

def session_date_match(session) -> bool:
    session_datetime = datetime.combine(session.date, session.course.lesson_time)
    session_endtime = session_datetime + timedelta(minutes=session.course.duration)

    time_now = datetime.now().time().strftime("%H:%M")
    date_match = session_datetime.date() == datetime.today().date() # session date match today
    start_match = time_now >= session_datetime.time().strftime("%H:%M") # time_now is after lesson start
    end_match = time_now <= session_endtime.time().strftime("%H:%M") # time_now is before lesson end

    if date_match and start_match and end_match:
        return True
    else:
        return False 