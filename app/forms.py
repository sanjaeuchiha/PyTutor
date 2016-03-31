from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, SelectField, TextAreaField, HiddenField, IntegerField, FormField, PasswordField, SelectMultipleField, FileField, DateTimeField, DecimalField, validators
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError
from app import db
from models import Room, Course, CourseType, User,ACTIVE_USER,INACTIVE_USER

DAYS = [
    ('', '-- Choose a Day --'),
    ('Mon', 'Mon'),
    ('Tues', 'Tues'),
    ('Wed', 'Wed'),
    ('Thur', 'Thur'),
    ('Fri', 'Fri'),
    ('Sat', 'Sat')
]

TIMES = [
    ("08-09[am]", "08-09[am]"),
    ("09-10[am]", "09-10[am]"),
    ("10-11[am]", "10-11[am]"),
    ("11-12[am]", "11-12[am]"),
    ("12-01[pm]", "12-01[pm]"),
    ("01-02[pm]", "01-02[pm]"),
    ("02-03[pm]", "02-03[pm]"),
    ("03-04[pm]", "03-04[pm]"),
    ("04-05[pm]", "04-05[pm]"),
    ("05-06[pm]", "05-06[pm]"),
    ("06-07[pm]", "06-07[pm]"),
    ("07-08[pm]", "07-08[pm]"),
    ("08-09[pm]", "08-09[pm]")
]

SEM = [
    ('', '-- Choose a Semester --'),
    ('1', 'Semester 1'),
    ('2', 'Semester 2'),
    ('3', 'Semester 3')
]

STATUS=[
    ('0','0'),
    ('1','1')
]

SALUTATION=[
    ('DR','DR'),
    ('MS','MS'),
    ('MR','MR'),
    ('MRS','MRS'),
    ('NA','NA'),
    ('TBA1','TBA1'),
    ('TBA2','TBA2')
]

ANSWER=[
    ('YES','YES'),
    ('NO','NO')
]


def getRooms():
    result = []
    result = [("", "-- Choose a Room --")]
    rooms = Room.query.order_by(Room.RoomId).all()
    for room in rooms:
        result.append((room.RoomId, room.RoomId))
    return result


def getCourses():
    result = []
    result = [("", "-- Choose a Course --")]
    courses = Course.query.order_by(Course.OtherCode).all()
    for course in courses:
        result.append((course.OtherCode, course.OtherCode))
    return result


def getCourseTypes():
    result = []
    result = [("", "-- Choose a Course Type --")]
    coursetypes = CourseType.query.order_by(CourseType.CourseType).all()
    for coursetype in coursetypes:
        result.append((coursetype.CourseType, coursetype.CourseType))
    return result


def getInitials():
    result = []
    result = [("", "-- Choose a User --")]
    users = User.query.order_by(User.firstname).all()
    for user in users:
        result.append((user.userInitial, user.firstname + ' '+user.lastname))
    return result


def getInitialsTutor():
    result = []
    result = [("", "-- Choose a User --")]
    users = User.query.filter_by(tutor='YES').order_by(User.firstname).all()
    for user in users:
        result.append((user.userInitial, user.firstname + ' '+user.lastname))
    return result


ROOMS = getRooms()
COURSES = getCourses()
COURSETYPES = getCourseTypes()
INITIALS = getInitials()
INITIALSTUTOR = getInitialsTutor()


class RegistrationForm(Form):
    firstname = TextField('firstname', [Required()])
    lastname = TextField('lastname', [Required()])
    email = TextField('email', [Required(), Email()])
    password = PasswordField('password', [Required()])
    confirm = PasswordField('confirmpassword', [
        Required(),
        EqualTo('password', message='Passwords must match')
    ])


class LoginForm(Form):
    email = TextField('email', [Required(), Email()])
    password = PasswordField('password', [Required()])

    remember_me = BooleanField('remember_me', default=False)


class EntryForm(Form):
    RoomId = SelectField('RoomId', choices=ROOMS, validators=[Required()])
    CourseCode = SelectField(
        'CourseCode',
        choices=COURSES,
        validators=[
            Required()])
    CourseType = SelectField(
        'CourseType',
        choices=COURSETYPES,
        validators=[
            Required()])
    UserInitial = SelectField(
        'UserInitial',
        choices=INITIALS,
        validators=[
            Required()])


class UploadForm(Form):
    filexl = FileField(validators=[Required()])


class MarkingForm(Form):
    CourseCode = SelectField(
        'CourseCode',
        choices=COURSES,
        validators=[
            Required()])
    UserInitial = SelectField(
        'UserInitial',
        choices=INITIALSTUTOR,
        validators=[
            Required()])
    SemesterId = SelectField('SemesterId', choices=SEM, validators=[Required()])
    AssignmentCode = TextField('AssignmentCode')
    AssignmentDue = DateTimeField(
        'AssignmentDue', validators=[
            validators.optional()])
    MarkingDue = DateTimeField(
        'AssignmentDue', validators=[
            validators.optional()])
    SubmissionNumber = IntegerField('SubmissionNumber', validators=[Required()])
    GradingRate = IntegerField('GradingRate', validators=[Required()])


class ChangePasswordForm(Form):
    oldpassword = PasswordField('oldpassword', [Required()])
    password = PasswordField('password', [Required()])
    confirm = PasswordField('confirm', [
        Required(),
        EqualTo('password', message='Passwords must match')
    ])

class ManageUserForm(Form):
    password = PasswordField('password')
    confirm=PasswordField('confirm',[EqualTo('password',message='Passwords must match')])
    status = SelectField('status',choices=STATUS,validators=[Required()])
    uwiId = TextField('uwiId',validators=[Required()])
    userInitial = TextField('userInitial',validators=[Required()])
    salutation = SelectField('salutation',choices=SALUTATION,validators=[Required()])
    marker = SelectField('marker',choices=ANSWER,validators=[Required()])
    tutor = SelectField('tutor',choices=ANSWER,validators=[Required()])
    lecturer = SelectField('lecturer',choices=ANSWER,validators=[Required()])
