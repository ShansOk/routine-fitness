from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import DailyForm, HomeForm, WeeklyForm, LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data/empty.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Disables modification notifications
app.config['SECRET_KEY'] = 'string'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
from models import Back, Chest, Arms, Legs, User

import random

@app.route('/login', methods =['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', title = 'Login', form=form)
    
@app.route('/register', methods = ['GET', 'POST'])
def new_user():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'New User {form.username.data} registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/', methods=['GET','POST'])
def home():
    form = HomeForm()
    if not form.validate_on_submit():
        return render_template('home.html', form=form)
    type_of_routine = form.type_of_routine.data
    if request.method == "POST" and type_of_routine == 'Daily Routine':
        return redirect(url_for("daily_routine"))
    elif request.method == "POST" and type_of_routine == 'Weekly Routine':
        return redirect(url_for("weekly_routine"))
    else:
        return render_template("home.html")

@app.route('/dailyroutine', methods=['GET','POST'])
def daily_routine():    
    form = DailyForm()
    if not form.validate_on_submit():
        return render_template('daily_routine.html', form=form)
    time = form.time.data
    muscle_group = form.muscle_group.data
    muscle1 = muscle_group[0]
    if len(muscle_group) != 1:
        muscle2 = muscle_group[1]
    else:
        muscle2 = muscle1

    if request.method == "POST":
        return redirect(url_for("one_workout", time=time, muscle1=muscle1, muscle2=muscle2))
    else: 
        return render_template("daily_routine.html")
    
@app.route("/<time>/<muscle1>/<muscle2>")
def one_workout(time, muscle1, muscle2):
    if time == 'Short (30 mins)':   #time selection
        no_of_exercises = 4
    elif time == 'Medium (1 hour)':
        no_of_exercises = 6
    elif time == 'Long (1 hour 30 mins)':
        no_of_exercises = 8

    list_of_exercises = []

    if muscle2 == muscle1:  # muscle group selection
        list = [muscle1]
    else:
        list = [muscle1, muscle2]

    for muscle in list:
        if muscle == 'Biceps' or muscle == 'Triceps' or muscle == 'Shoulders':  # Calling rows for biceps
            arm_subgroup = Arms.query.filter(Arms.arm_subgroup == muscle).all()
            no_of_rows = len(arm_subgroup)
        else:   # else rows for all else
            no_of_rows = eval(muscle).query.count()

        if len(list) == 1:  # link to muscle group/time selectors
            random_sample = random.sample(range(1, no_of_rows + 1), min(no_of_exercises, no_of_rows))
        else:
            random_sample = random.sample(range(1, no_of_rows + 1), min(int(no_of_exercises/2), no_of_rows))
            
        for i in random_sample: #
            if muscle =='Biceps' or muscle == 'Triceps' or muscle == 'Shoulders':
                random_exercise = arm_subgroup[i-1]
            else:
                random_exercise = eval(muscle).query.get(i)    #random_exercise = biceps[i-1].exercise_name
            list_of_exercises.append(random_exercise.exercise_name)
            one_workout = str(list_of_exercises)[1:-1].replace(",", "<br/>").replace("'", "") # multiline list and removal of ,'[]

    return render_template('one_workout.html', title='One Workout') + f'{one_workout}' + f"<h1>{time}</h1>"


@app.route('/weeklyroutine', methods=['GET', 'POST'])
def weekly_routine():
    form = WeeklyForm()
    if not form.validate_on_submit():
        return render_template('weekly_routine.html', form=form)
    days = form.days.data
    print(days)
    if request.method == "POST":
        return redirect(url_for("routine", days=days))
    else: 
        return render_template("weekly_routine.html")

@app.route("/<days>")
def routine(days):
    no_of_muscle_groups = 6 // int(days[0])
    no_of_exercises = int(days[0])
    list_of_exercises = []
    if days == '2 days' or days == '3 days':
        repeat = [1]
    elif days == '4 days' or '6 days':
        repeat = [1, 2]

    if days == '2 days' or days == '4 days':
        muscle_group1 = ['Back', 'Biceps', 'Shoulders']
        muscle_group2 = ['Chest', 'Triceps', 'Legs']
        muscle_group3 = []
        sample_size = 2
    elif days == '3 days' or days == '6 days':
        muscle_group1 = ['Back', 'Biceps']
        muscle_group2 = ['Chest', 'Triceps']
        muscle_group3 = ['Legs', 'Shoulders'] 
        sample_size = 3

    for j in repeat:
        for muscle_group in [muscle_group1, muscle_group2, muscle_group3]: #[muscles]
            for muscle in muscle_group:   #muscles
                if muscle == 'Biceps' or muscle == 'Triceps' or muscle == 'Shoulders':  # Calling rows for biceps
                    arm_subgroup = Arms.query.filter(Arms.arm_subgroup == muscle).all()
                    no_of_rows = len(arm_subgroup)
                else:   # else rows for all else
                    no_of_rows = eval(muscle).query.count()
                random_sample = random.sample(range(1, no_of_rows + 1), sample_size)
                for i in random_sample: #
                    if muscle == 'Biceps' or muscle == 'Triceps' or muscle == 'Shoulders':
                        random_exercise = arm_subgroup[i-1]
                    else:
                        random_exercise = eval(muscle).query.get(i)    #random_exercise = biceps[i-1].exercise_name
                    list_of_exercises.append(random_exercise.exercise_name)
                    routine = str(list_of_exercises)[1:-1].replace(",", "<br/>").replace("'", "")

    return render_template('routine.html', title='Your Routine') + f'{routine}' + f"<h1>{days}</h1>"
