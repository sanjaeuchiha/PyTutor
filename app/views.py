from flask import render_template, jsonify
from app import app,db,lm
from models import EntryClone,User, ROLE_ADMIN,INACTIVE_USER,CourseType,Room,Marking
from forms import RegistrationForm,LoginForm, EntryForm,UploadForm,MarkingForm,ChangePasswordForm,ManageUserForm
from werkzeug import check_password_hash, generate_password_hash, secure_filename
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, send_from_directory, abort
import uuid
from flask.ext.login import login_user, logout_user, current_user, login_required
from config import ALLOWED_EXTENSIONS
from functools import wraps
import os,csv
import time as pytime


def active_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.status==INACTIVE_USER:
            flash("Please wait for activation",category='danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(413)
def internal_error(error):
    db.session.rollback()
    return render_template('413.html'), 413


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('There is already a user with this email!', category='danger')
            return redirect(url_for('register'))
        user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            password=generate_password_hash(
                form.password.data))
        db.session.add(user)
        db.session.commit()
        flash(
            'Thanks for registering. Your account will need activation.',
            category='info')
        return redirect(url_for('login'))
    return render_template(
        'register.html',
        title='Register',
        form=form,
        )

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def login():
    #if g.user is not None:
    #if g.user is not None and g.user.is_authenticated():
        #return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash(
                'The username or password you entered is incorrect!',
                category='danger')
            return redirect(url_for('login'))
        if user.password is None or user.password == "":
            flash(
                'The username or password you entered is incorrect!',
                category='danger')
            return redirect(url_for('login'))
        if user and check_password_hash(user.password, form.password.data) and user.is_active():
            session['remember_me'] = form.remember_me.data
            if 'remember_me' in session:
                remember_me = session['remember_me']
                session.pop('remember_me', None)
            login_user(user, remember=remember_me)
            flash('You have successfully logged in', category='success')
            return redirect(request.args.get('next') or url_for('timetable',sem='1'))

        if user and not check_password_hash(user.password, form.password.data) and user.is_active():
            flash('Please check your username and password!', category='danger')
            return redirect(url_for('login'))

        if user and check_password_hash(user.password, form.password.data) and not user.is_active():
            flash("Your account needs activation!", category='warning')
            return redirect(url_for('login'))

        if user and not check_password_hash(user.password, form.password.data) and not user.is_active():
            flash("Your account needs activation!", category='warning')
            return redirect(url_for('login'))

    return render_template('login.html',
                           title='Sign In',
                           form=form)



@app.route('/timetable/<sem>',methods=['GET'])
@login_required
@active_required
def timetable(sem):
    if not sem:
        sem = 1
    title="Time Table"
    days=['Mon','Tues','Wed','Thur','Fri','Sat']
    timeDict={}
    times =  ["08-09[am]","09-10[am]","10-11[am]","11-12[am]","12-01[pm]","01-02[pm]","02-03[pm]","03-04[pm]","04-05[pm]","05-06[pm]","06-07[pm]","07-08[pm]","08-09[pm]"]

    entry_count=0
    tuthours=0
    entries = EntryClone.query.filter_by(userInitial=g.user.userInitial,SemesterId=sem)
    entries = entries.filter((EntryClone.CourseType=='TUTA') | (EntryClone.CourseType=='TUTB')).all()
    for e in entries:
        if e.CourseCode=='COMP1127':
            pass
        else:
            entry_count=entry_count + 1

    tuthours=entry_count


    markhours=0
    markings = Marking.query.filter_by(userInitial=g.user.userInitial,SemesterId=sem).all()
    for m in markings:
        markhours = markhours + (m.SubmissionNumber*m.GradingRate)/60.0


    lecthours=0
    lectures = EntryClone.query.filter_by(userInitial=g.user.userInitial,SemesterId=sem,CourseType='LEC').all()
    for l in lectures:
        if l.CourseCode=='COMP1127':
            pass
        lecthours=lecthours + 1

    labhours=0
    labs = EntryClone.query.filter_by(userInitial=g.user.userInitial,SemesterId=sem,CourseType='LAB').all()
    for b in labs:
        if b.CourseCode=='COMP1127':
            pass
        labhours=labhours+1

    buttonclicked = request.args.get("btn")
    if buttonclicked:
        edit=True
    else:
        edit=False


    tutorial = request.args.get("tutorial")


    for index, time in enumerate(times):
        tempDict={}
        for day in days:
            tempList=[]
            if tutorial:
                values = EntryClone.query.filter_by(EntryTime=time,EntryDay=day,SemesterId=sem)
                values = values.filter((EntryClone.CourseType=='LAB') | (EntryClone.CourseType=='TUTA') | (EntryClone.CourseType=='TUTB')).all()
            if not tutorial and g.user.lecturer == 'YES' :
                values = EntryClone.query.filter_by(EntryTime=time,EntryDay=day,SemesterId=sem).all()
            if g.user.tutor == 'YES':
                values = EntryClone.query.filter_by(EntryTime=time,EntryDay=day,SemesterId=sem)
                values = values.filter((EntryClone.CourseType=='LAB') | (EntryClone.CourseType=='TUTA') | (EntryClone.CourseType=='TUTB')).all()
            for value in values:
                entry = dict()
                entry["ID"]=value.EntryID
                entry["CourseCode"]=value.CourseCode
                entry["Person"]=value.userInitial
                entry["Room"]=value.RoomId
                entry["CourseType"]=value.CourseType
                tempList.append(entry)
            tempDict[day]=tempList
        timeDict[time] = tempDict

    return render_template('timetable.html',title=title,times=times,timeDict=timeDict,days=days,edit=edit,sem=sem,tut=tutorial,tuthours=tuthours,markhours=markhours,labhours=labhours,lecthours=lecthours)


@app.route('/addMarker',methods=['GET','POST'])
@login_required
@active_required
def addMarker():
    title="Add Marker"
    user  = User.query.get_or_404(g.user.id)
    #markers = Marking.query.all()
    markers = db.session.query(Marking,User).filter(Marking.userInitial==User.userInitial).all()
    if user.role != ROLE_ADMIN:
            flash('Sorry. You need special permissions to carry out this task!', category='danger')
            abort(404)

    form=MarkingForm()

    if form.validate_on_submit():

        entry = Marking(
                CourseCode=form.CourseCode.data,
                userInitial=form.UserInitial.data,
                SemesterId=form.SemesterId.data,
                AssignmentCode=form.AssignmentCode.data,
                AssignmentDue=form.AssignmentDue.data,
                MarkingDue=form.AssignmentDue.data,
                SubmissionNumber=form.SubmissionNumber.data,
                GradingRate = form.GradingRate.data
                )
        db.session.add(entry)
        db.session.commit()
        flash('Marker Added', category='success')
        redirect(url_for('addMarker'))
    return render_template('addmarker.html',title=title,form=form,markers=markers)



@app.route('/add/<time>/<day>/<sem>',methods=['GET','POST'])
@login_required
@active_required
def add(time,day,sem):
    title="Add Entry"
    user  = User.query.get_or_404(g.user.id)
    entry = EntryClone.query.filter_by(EntryDay=day,EntryTime=time,SemesterId=sem)

    if user.role != ROLE_ADMIN:
            flash('Sorry. You need special permissions to carry out this task!', category='danger')
            abort(404)


    form=EntryForm()

    if form.validate_on_submit():
        for e in entry:
            if (e.userInitial == form.UserInitial.data):
                flash('Sorry. You already have an entry in this slot!', category='danger')
                myurl=app.config["SERVER_BASE"]+"/timetable/"+sem+"?tutorial=&btn=edit"
                return redirect(myurl)

            if (e.RoomId == form.RoomId.data):
                flash('Sorry. This room is already occupied!', category='danger')
                myurl=app.config["SERVER_BASE"]+"/timetable/"+sem+"?tutorial=&btn=edit"
                return redirect(myurl)

        entry = EntryClone(
                EntryDay=day,
                EntryTime=time,
                RoomId=form.RoomId.data,
                SemesterId=sem,
                CourseCode=form.CourseCode.data,
                CourseType=form.CourseType.data,
                userInitial=form.UserInitial.data
                )
        db.session.add(entry)
        db.session.commit()
        flash('Slot Added', category='success')
        myurl=app.config["SERVER_BASE"]+"/timetable/"+entry.SemesterId+"?tutorial=&btn=edit"
        return redirect(myurl)
    return render_template('add.html',title=title,form=form,time=time,day=day,sem=sem)


@app.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def edit(id):
    title="Edit Entry"
    user  = User.query.get_or_404(g.user.id)
    entry = EntryClone.query.get_or_404(id)
    if not entry:
        abort(404)

    if (user.userInitial != entry.userInitial) and user.role != ROLE_ADMIN :
        flash('You are not allowed to edit this entry!', category='danger')
        return redirect(url_for('timetable',sem=entry.SemesterId))

    form=EntryForm()
    if form.validate_on_submit():
        entry.RoomId=form.RoomId.data
        entry.CourseCode=form.CourseCode.data
        entry.CourseType=form.CourseType.data
        entry.UserInitial=form.UserInitial.data
        db.session.add(entry)
        db.session.commit()
        flash('Slot Edited', category='success')
        myurl =app.config["SERVER_BASE"]+"/timetable/"+entry.SemesterId+"?tutorial=&btn=edit"
        #return redirect(url_for('timetable',sem=entry.SemesterId))
        return redirect(myurl)
    else:
        form.RoomId.data = entry.RoomId
        form.CourseCode.data = entry.CourseCode
        form.CourseType.data = entry.CourseType
        form.UserInitial.data = entry.userInitial
    return render_template('edit.html',id=id,title=title,form=form)


@app.route('/delete/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def delete(id):
    user  = User.query.get_or_404(g.user.id)
    entry = EntryClone.query.get_or_404(id)
    if not entry:
        abort(404)

    if (user.userInitial != entry.userInitial) and user.role != ROLE_ADMIN:
        flash('You are not allowed to delete this entry!', category='danger')
        abort(404)

    db.session.delete(entry)
    db.session.commit()
    flash('Entry Successfully Deleted!', category='success')
    #return redirect(url_for('timetable',sem=entry.SemesterId))
    myurl =app.config["SERVER_BASE"]+"/timetable/"+entry.SemesterId+"?tutorial=&btn=edit"
    return redirect(myurl)

@app.route('/deleteT/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def deleteT(id):
    user  = User.query.get_or_404(g.user.id)
    entry = EntryClone.query.get_or_404(id)
    if not entry:
        abort(404)

    if (user.userInitial != entry.userInitial):
        flash('You are not allowed to delete this entry!', category='danger')
        return redirect(url_for('timetable',sem=entry.SemesterId))

    entry.userInitial="TUTOR"
    db.session.add(entry)
    db.session.commit()

    flash('Your Entry was successfully removed!', category='success')
    myurl =app.config["SERVER_BASE"]+"/timetable/"+entry.SemesterId+"?btn=edit"
    return redirect(myurl)
    #return redirect(url_for('timetable',sem=entry.SemesterId))


@app.route('/addT/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def addT(id):
    user  = User.query.get_or_404(g.user.id)
    entry = EntryClone.query.get_or_404(id)
    if not entry:
        abort(404)
    if (entry.userInitial != "TUTOR"):
        flash('You are not allowed to add to this entry!', category='danger')
        return redirect(url_for('timetable',sem=entry.SemesterId))

    entry.userInitial=user.userInitial
    db.session.add(entry)
    db.session.commit()
    flash('Your Entry was successfully added!', category='success')
    myurl=app.config["SERVER_BASE"]+"/timetable/"+entry.SemesterId+"?btn=edit"
    return redirect(myurl)
    #return redirect(url_for('timetable',sem=entry.SemesterId))

@app.route('/deleteMarker/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def deleteMarker(id):
    user  = User.query.get_or_404(g.user.id)

    if user.role != ROLE_ADMIN:
        flash('You are not allowed to perform this operation!', category='danger')
        abort(404)

    entry = Marking.query.get_or_404(id)

    if not entry:
        abort(404)

    db.session.delete(entry)
    db.session.commit()
    flash('Entry Successfully Deleted!', category='success')
    return redirect(url_for('addMarker'))


@app.route('/deleteuser/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def deleteuser(id):
    user  = User.query.get_or_404(id)
    entries = EntryClone.query.filter_by(userInitial=user.userInitial).all()
    markers = Marking.query.filter_by(userInitial=user.userInitial).all()

    if not user:
        abort(404)
    if (g.user.role != 1):
        flash('You are not allowed to delete this entry!', category='danger')
        return redirect(url_for('manageusers'))


    if entries:
       for entry in entries:
           db.session.delete(entry)
           db.session.commit()

    if markers:
        for marker in markers:
            db.session.delete(marker)
            db.session.commit()


    db.session.delete(user)
    db.session.commit()

    flash('Your Entry was successfully removed!', category='success')
    return redirect(url_for('manageusers'))



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def timeDifference(start_time,end_time):
        timeString1 = "03/06/05 " + start_time
        timeTuple1 = pytime.strptime(timeString1, "%m/%d/%y %I:%M %p")
        timeString2 = "03/06/05 " + end_time
        timeTuple2 = pytime.strptime(timeString2, "%m/%d/%y %I:%M %p")
        time_difference = pytime.mktime(timeTuple2)+60 - pytime.mktime(timeTuple1)
        return int(time_difference/(60.0*60))

def delEntryClone(sem):
    entrydel = EntryClone.query.filter_by(SemesterId=sem).all()
    for e in entrydel:
        db.session.delete(e)
        db.session.commit()



@app.route('/upload',methods=['GET','POST'])
@login_required
def uploadXL():

    times =  ["08-09[am]","09-10[am]","10-11[am]","11-12[am]","12-01[pm]","01-02[pm]","02-03[pm]","03-04[pm]","04-05[pm]","05-06[pm]","06-07[pm]","07-08[pm]","08-09[pm]"]

    timesDict =  {
        "8:00AM":"08-09[am]",
        "9:00AM":"09-10[am]",
        "10:00AM":"10-11[am]",
        "11:00AM":"11-12[am]",
        "12:00PM":"12-01[pm]",
        "1:00PM":"01-02[pm]",
        "2:00PM":"02-03[pm]",
        "3:00PM":"03-04[pm]",
        "4:00PM":"04-05[pm]",
        "5:00PM":"05-06[pm]",
        "6:00PM":"06-07[pm]",
        "7:00PM":"07-08[pm]",
        "8:00PM":"08-09[pm]"
        }


    form = UploadForm()
    title="Upload File"
    filename = ""
    file=None
    if form.validate_on_submit():
        file = request.files['filexl']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(uuid.uuid4()) + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Only CSV Files Allowed', category='danger')
            return redirect(url_for('uploadXL'))

        #filepath = "/home/dundee/Computing2.csv"
        filepath = app.config['UPLOAD_FOLDER']+"/"+filename
        f = open(filepath,'rb')

        readerDict = csv.DictReader(f, delimiter='\t', dialect='excel')
        #This count variable is to just decide when to delete entries for the semester
        count=0
        for key in readerDict:
            entry_time=""
            entry_room=""
            entry_sem=""
            entry_type=""
            entry_initial=""
            entry_course=""
            entry_type=""

            entry_room = Room.query.filter_by(RoomNameSRU=key['ROOM_DESC']).first()
            if entry_room:
                entry_room = entry_room.RoomId
            else:
                entry_room="_MIA"

            entry_sem=key['SEM_OFFERED'][4]
            if entry_sem:
                entry_sem=entry_sem
                if count == 0:
                    delEntryClone(entry_sem)
            else:
                entry_sem="_MIA"

            entry_initial = User.query.filter_by(uwiId=key['STAFF_ID']).first()
            if entry_initial:
                entry_initial=entry_initial.userInitial
            else:
                entry_initial="_MIA"

            entry_type = CourseType.query.filter_by(CourseTypeDesc=key['SCHED_TYPE']).first()
            if entry_type:
                entry_type= entry_type.CourseType
            else:
                entry_type="_MIA"

            entry_day=key['DAY']
            if entry_day:
                entry_day=entry_day
            else:
                entry_day="MIA"

            entry_course=key['SUBJ_CODE']+key['CRSE_NUMB']
            if entry_course:
                entry_course=entry_course
            else:
                entry_course="_MIA"

            entry_time=key['START_TIME'].strip().replace(' ','')
            if entry_time:
                entry_time=timesDict[entry_time]
            else:
                entry_time="_MIA"


            timeDiff=timeDifference(key['START_TIME'].strip(),key['END_TIME'].strip())
            print timeDiff

            indx = times.index(entry_time)
            for i in range(timeDiff):
                entry = EntryClone(
                    EntryDay=entry_day,
                    EntryTime=times[indx+i],
                    RoomId=entry_room,
                    SemesterId=entry_sem,
                    CourseCode=entry_course,
                    CourseType=entry_type,
                    userInitial=entry_initial
            )
                db.session.add(entry)
                db.session.commit()


            count = count + 1

        flash('File Successfully Uploaded', category='success')
        return redirect(url_for('timetable',sem=entry_sem))

    return render_template('upload.html',title=title,form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out!', category='success')
    return redirect(url_for('login'))

@app.route('/changepassword',methods=['GET','POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    title="Change Password"
    user  = User.query.get_or_404(g.user.id)
    if form.validate_on_submit():
            if check_password_hash(g.user.password, form.oldpassword.data):
                g.user.password = generate_password_hash(form.password.data)
                db.session.add(g.user)
                db.session.commit()
                flash('Your password was successfully changed!', category='success')
                return redirect(url_for('changepassword'))
            else:
                flash("Your old password is incorrect!", category='danger')
                return redirect(url_for('changepassword'))
    return render_template('changepassword.html',title=title,form=form,user=user)



@app.route('/manageusers',methods=['GET','POST'])
@login_required
def manageusers():
    title="Manage Users"
    useradmin  = User.query.get_or_404(g.user.id)
    if useradmin.role != ROLE_ADMIN:
        flash('Sorry. You need special permissions to carry out this task!', category='danger')
        abort(404)

    users  = User.query.all()
#    if form.validate_on_submit():
#            if check_password_hash(g.user.password, form.oldpassword.data):
#                g.user.password = generate_password_hash(form.password.data)
#                db.session.add(g.user)
#                db.session.commit()
#                flash('Your password was successfully changed!', category='success')
#                return redirect(url_for('changepassword'))
#            else:
#                flash("Your old password is incorrect!", category='danger')
#                return redirect(url_for('changepassword'))
    return render_template('manageusers.html',title=title,users=users)

@app.route('/edituser/<int:id>',methods=['GET','POST'])
@login_required
@active_required
def edituser(id):
    title="Edit User"
    user  = User.query.get_or_404(id)
    if not user:
        abort(404)

    if g.user.role != ROLE_ADMIN :
        flash('You are not allowed to edit users!', category='danger')
        return redirect(url_for('manageusers'))

    form=ManageUserForm()
    if form.validate_on_submit():
        if form.password.data and form.confirm.data:
            user.password=generate_password_hash(form.password.data)
        user.status = form.status.data
        user.uwiId=form.uwiId.data
        user.userInitial=form.userInitial.data
        user.salutation=form.salutation.data
        user.marker=form.marker.data
        user.tutor=form.tutor.data
        user.lecturer=form.lecturer.data
        db.session.add(user)
        db.session.commit()
        flash('User Successfully Edited', category='success')
        return redirect(url_for('manageusers'))
    else:
        form.status.data = str(user.status)
        form.uwiId.data = user.uwiId
        form.userInitial.data = user.userInitial
        form.salutation.data = user.salutation
        form.marker.data = user.marker
        form.tutor.data = user.tutor
        form.lecturer.data  = user.lecturer
    return render_template('edituser.html',id=id,title=title,form=form)


@app.route('/recipes')
def get_recipes():
    recipes=[
            {
                "id":1,
                "name": "Curry Veggie Chunks",
                "serving":3,
                "description":"Nice Golden Veggie Chunks",
                "ingredient":[" 4LB Chunks","3 Packs Curry"],
                "instructions":["1. Boil Chunks","2. Drain","3. Mix in Curry"]
            },
            {
                "id":2,
                "name": "Stew Veggie Chunks",
                "serving":4,
                "description":"Brown Stew Veggie Chunks",
                "ingredient":[" 4LB Chunks","3 Cups Ketchup"],
                "instructions":["1. Boil Chunks","2. Drain","3. Mix in Ketchup"]
            }
    ]
    return jsonify({'recipes': recipes})
