# coding: utf-8
from hashlib import md5
from app import db
from app import app

ROLE_USER = 0
ROLE_ADMIN = 1
ACTIVE_USER = 1
INACTIVE_USER = 0


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(140))
    status = db.Column(db.SmallInteger, default=INACTIVE_USER)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    uwiId = db.Column(db.String(8))
    userInitial = db.Column(db.String(9))
    salutation = db.Column(db.Enum(u'DR', u'MS', u'MR', u'MRS',u'NA', u'TBA1', u'TBA2'))
    marker = db.Column(db.Enum(u'YES',u'NO'))
    tutor = db.Column(db.Enum(u'YES',u'NO'))
    lecturer = db.Column(db.Enum(u'YES',u'NO'))

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.status == ACTIVE_USER 

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.email)

    
class AssignmentType(db.Model):
    AssignmentCode = db.Column(db.String(3), primary_key=True)
    Description = db.Column(db.String(100))


class Course(db.Model):
    CourseCode = db.Column(db.String(14), primary_key=True)
    CourseName = db.Column(db.String(50))
    OtherCode = db.Column(db.String(14))


class CourseType(db.Model):
    CourseType = db.Column(db.String(8), primary_key=True)
    CourseTypeDesc = db.Column(db.String(25))


class EntryClone(db.Model):
    EntryID = db.Column(db.Integer, primary_key=True)
    EntryDay = db.Column(db.String(4))
    EntryTime = db.Column(db.String(9))
    RoomId = db.Column(db.String(10))
    SemesterId = db.Column(db.String(1))
    CourseCode = db.Column(db.String(14))
    CourseType = db.Column(db.String(8))
    userInitial = db.Column(db.String(9))
    Delta = db.Column(db.Enum(u'VAL', u'ADD', u'MOD', u'DEL'), default='VAL')


class HashFile(db.Model):

    FileHash = db.Column(db.String(100), primary_key=True)
    FileTime = db.Column(db.Integer)
    Filename = db.Column(db.String(100))
    FileSem = db.Column(db.String(1))



class Marking(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    CourseCode = db.Column(db.String(14))
    userInitial = db.Column(db.String(9))
    SemesterId = db.Column(db.String(1))
    AssignmentCode = db.Column(db.String(3))
    AssignmentDue = db.Column(db.DateTime)
    MarkingDue = db.Column(db.DateTime)
    SubmissionNumber = db.Column(db.Integer)
    GradingRate = db.Column(db.Integer)

    #FIXME:fix submission and less than 60
    def calculateHours(self):
        if self.SubmissionNumber and self.GradingRate:
            return (self.SubmissionNumber*self.GradingRate)/60.0
        return 0 


class Room(db.Model):
    RoomId = db.Column(db.String(10), primary_key=True)
    RoomName = db.Column(db.String(50))
    RoomNameSRU = db.Column(db.String(50))
    RoomType =db.Column(db.Enum(u'TUTROOM', u'LECROOM', u'LABROOM', u''))


class Semester(db.Model):
    SemesterId = db.Column(db.String(1), primary_key=True)
    SemesterDesc = db.Column(db.String(50))
