from flask import Flask, render_template, url_for, request, session, redirect, flash, current_app as app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo, pymongo
# from flask.ext.pymongo import PyMongo
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from flask_mongoengine import MongoEngine, Document
import os
import json
import datetime
from bson.objectid import ObjectId


class JSONEncoder(json.JSONEncoder):
    
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# import urllib

# db_url = urllib.parse.quote('mongodb://user:user123@ds033499.mongolab.com:33499/enron')

# client = MongoClient(db_url)

app = Flask(__name__)

#app.config['MONGO_DBNAME'] = 'test'
#app.config['MONGO_URI'] = 'mongodb://justincletus:WsP6oB5Fz4CT3L87@cluster0-shard-00-00-steym.gcp.mongodb.net:27017,cluster0-shard-00-01-steym.gcp.mongodb.net:27017,cluster0-shard-00-02-steym.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority'

app_db = MongoEngine(app)
#app.config['SECRET_KEY'] = 'ab89559b-8998-4cca-889a-e5b889a9db18'

client = pymongo.MongoClient("mongodb://justincletus:WsP6oB5Fz4CT3L87@cluster0-shard-00-00-steym.gcp.mongodb.net:27017,cluster0-shard-00-01-steym.gcp.mongodb.net:27017,cluster0-shard-00-02-steym.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
mongo = client.test

# app_secret key = e867e2cebdfc44d59bfc3e16f4c28379

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Student(UserMixin, app_db.Document):
    meta = {'collection': 'students'}
    name = app_db.StringField(max_length=30)
    password = app_db.StringField()
    

@login_manager.user_loader
def user_loader(id):
    user = SessionUser.find_by_session_id(id)
    if user is None:
        flash("you have been automatically logout")
    return user
# def user_loader(user_id):
#     return SessionUser.find_by_session_id(user_id)
# def load_user(user_id):
#     return Student.objects(pk=user_id).first()
    

# mongo = PyMongo(db)

@app.route('/')
def index():
    # print(session)
    if 'username' in session:
        username = session['username']
        #return redirect(url_for('dashboard', username=username))
        # print(username)
        return render_template('dashboard.html', username=username)
        # return 'You are logged in as ' + session['username']

    return render_template("index.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    
    
    if request.method == 'GET':
        if 'username' in session:
            # del session['username']
            # return 'I am logged out'
            user = session['username']
            
            print(user, 'I am here')
            # print(request.url)
            #return redirect(request.url)
            return redirect(url_for('index'))
            
            # return "dashboard"   
    
    if request.method == 'POST':
        
        users = mongo.db.students
        #user = SessionUser.fin_by_session_id(request.data['user_id'])
        # user = users.SessionUser.find_by_session_id(request.data['user_id'])
        
        user_pass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
        existing_pass = users.find_one({'password': user_pass})
        if existing_pass:
            print("Password is correct")
            
        login_user = users.find_one({'name' : request.form['username']})
        

        if login_user:
            # and (login_user['password'] == user_pass
            # if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            if (login_user['name'] == request.form['username']):
                session['username'] = request.form['username']
                username = session['username']
                return render_template('index.html', username=username)
                # return "I am here"
                # return redirect(url_for('dashboard'))
                # return "Login to dashboard"
            
        #return "I am here"
        return render_template('login.html')
            
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        students = mongo.db.students
        existing_user = students.find_one({'name': request.form['username']})
        # users = mongo.db.users
        # existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            students.insert({'fullname': request.form['fullname'], 'roll_number': request.form['roll_number'], 'name' : request.form['username'], 'standard': request.form['standard'], 'password' : hashpass})
            session['username'] = request.form['username']
            #return redirect(request.url)
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/logout')
# @login_required
def logout():
    
    logout_user()
    del session['username']
    return redirect(url_for('index'))

    
@app.route('/dashboard')
@login_required
def dashboard():    
    print(session['username'])
    return "Dashboard Page"


@app.route('/records', methods=['GET', 'POST'])
def records():
    username = session['username']
    if username is None:
        return redirect(url_for('login'))
    
    # if current_user.is_authenticated() == True:
    #     print(current_user.get_id())
    user = mongo.db.students
    user_id = user.find_one({'name': username})
    
    standards = user_id['standard']
    
    if request.method == 'POST':
        data = mongo.db.records
        std = request.form['standard']
        grade = request.form['grade']
        remark = request.form['remark']
        percentage = request.form['percentage']
        data.insert({'user_id': user_id['_id'], 'standard': std, 'grade': grade, 'remark': remark, 'percentage': percentage})
        flash("Record inserted!")
        
        print(user_id['_id'])
        return redirect(url_for('index'))
         
    
    #return redirect(url_for('records', standards=standards))
    
    return render_template("records.html", username=username, standards=int(standards))

if __name__ == '__main__':
    app.secret_key = 'ab89559b-8998-4cca-889a-e5b889a9db18'
    app.run(debug=True)

