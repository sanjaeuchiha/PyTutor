#!flask/bin/python
import csv
import hashlib
from app import app, db
from app.models import EntryClone, User, Course, CourseType, Room, Semester
import time as pytime


def timeDifference(start_time, end_time):
    timeString1 = "03/06/05 " + start_time
    timeTuple1 = pytime.strptime(timeString1, "%m/%d/%y %I:%M %p")
    timeString2 = "03/06/05 " + end_time
    timeTuple2 = pytime.strptime(timeString2, "%m/%d/%y %I:%M %p")
    time_difference = pytime.mktime(timeTuple2)+60 - pytime.mktime(timeTuple1)
    return int(time_difference/(60.0*60))

times = [
    "08-09[am]",
    "09-10[am]",
    "10-11[am]",
    "11-12[am]",
    "12-01[pm]",
    "01-02[pm]",
    "02-03[pm]",
    "03-04[pm]",
    "04-05[pm]",
    "05-06[pm]",
    "06-07[pm]",
    "07-08[pm]",
     "08-09[pm]"]

timesDict = {
    "8:00AM": "08-09[am]",
    "9:00AM": "09-10[am]",
    "10:00AM": "10-11[am]",
    "11:00AM": "11-12[am]",
    "12:00PM": "12-01[pm]",
    "1:00PM": "01-02[pm]",
    "2:00PM": "02-03[pm]",
    "3:00PM": "03-04[pm]",
    "4:00PM": "04-05[pm]",
    "5:00PM": "05-06[pm]",
    "6:00PM": "06-07[pm]",
    "7:00PM": "07-08[pm]",
    "8:00PM": "08-09[pm]"
    }


filepath = "/home/dundee/Desktop/timetable.csv"
f = open(filepath, 'rb')

readerDict = csv.DictReader(f, delimiter='\t', dialect='excel')
for key in readerDict:
    #print key['TUESDAY']
    t = key['TUESDAY']
    t = t.split("\"")
    print key['TIME']
    print t[0].split("\n")[0].strip()
    #for s in t:
        #v= t.split("\n").split(",")
        #print s
        #entry_time =key['TIME']
        #entry_room = ""
        #entry_sem = ""
        #entry_type = ""
        #entry_initial = ""
        #entry_course = ""
        #entry_type = ""

    #entry_room = Room.query.filter_by(RoomNameSRU=key['ROOM_DESC']).first()
    #if entry_room:
        #entry_room = entry_room.RoomId
    #else:
        #entry_room = "_MIA"

    #entry_sem = key['SEM_OFFERED'][4]
    #if entry_sem:
        #entry_sem = entry_sem
    #else:
        #entry_sem = "_MIA"

    #entry_initial = User.query.filter_by(uwiId=key['STAFF_ID']).first()
    #if entry_initial:
        #entry_initial = entry_initial.userInitial
    #else:
        #entry_initial = "_MIA"

    #entry_type = CourseType.query.filter_by(
        #CourseTypeDesc=key['SCHED_TYPE']).first()
    #if entry_type:
        #entry_type = entry_type.CourseType
    #else:
        #entry_type = "_MIA"

    #entry_day = key['DAY']
    #if entry_day:
        #entry_day = entry_day
    #else:
        #entry_day = "MIA"

    #entry_course = key['SUBJ_CODE']+key['CRSE_NUMB']
    #if entry_course:
        #entry_course = entry_course
    #else:
        #entry_course = "_MIA"

    entry_time = key['TIME']
    if entry_time:
        entry_time = entry_time
    else:
        entry_time = "_MIA"


    #entry = EntryClone(
        #EntryDay=entry_day,
        #EntryTime=entry_time,
        #RoomId=entry_room,
        #SemesterId=entry_sem,
        #CourseCode=entry_course,
        #CourseType=entry_type,
        #userInitial=entry_initial
        #)
    #db.session.add(entry)
    #db.session.commit()
