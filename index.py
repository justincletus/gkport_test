from flask import Flask, render_template, url_for, request, session, redirect, flash, current_app as app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo, pymongo
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from flask_mongoengine import MongoEngine, Document
import os
import json
import datetime
from bson.objectid import ObjectId


app = Flask(__name__)

app_db = MongoEngine(app)

client = pymongo.MongoClient("mongodb://justincletus:WsP6oB5Fz4CT3L87@cluster0-shard-00-00-steym.gcp.mongodb.net:27017,cluster0-shard-00-01-steym.gcp.mongodb.net:27017,cluster0-shard-00-02-steym.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
mongo = client.test

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
        
    return render_template("index.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    
    
    if request.method == 'GET':
        if 'username' in session:
            user = session['username']
            return redirect(url_for('index'))   
    
    if request.method == 'POST':
        
        users = mongo.db.students
        
        user_pass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
        existing_pass = users.find_one({'password': user_pass})
        
        print(user_pass)
        print(existing_pass)
            
        login_user = users.find_one({'name' : request.form['username']})
        

        if login_user:
            # and (login_user['password'] == user_pass
            # if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            if (login_user['name'] == request.form['username']):
                session['username'] = request.form['username']
                username = session['username']
                return render_template('index.html', username=username)
                
        return render_template('login.html')
            
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        students = mongo.db.students
        existing_user = students.find_one({'name': request.form['username']})
        

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            students.insert({'fullname': request.form['fullname'], 'roll_number': request.form['roll_number'], 'name' : request.form['username'], 'standard': request.form['standard'], 'password' : hashpass})
            session['username'] = request.form['username']
            
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/logout')
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
    error = None
    username = session['username']
    if username is None:
        return redirect(url_for('login'))
    user = mongo.db.students
    user_id = user.find_one({'name': username})
    
    standards = user_id['standard']
    
    if request.method == 'POST':
        data = mongo.db.records
        std = request.form['standard']
        if int(std) >= int(standards):
            error = "You can't insert record greater then your current standard!"
            flash("You can't insert record greater then or equal to your current standard!")
            return redirect(url_for('records', error=error))
        elif (int(std) < 2) and (int(standards) ==1):
            flash("You can't insert record because your current standard is %s"%standards)
            return redirect(url_for('records'))
            
        grade = request.form['grade']
        remark = request.form['remark']
        percentage = request.form['percentage']
        existing_record = data.find_one({'standard': std})
        if not existing_record is None:
            error = "You can't insert dublicate record!"            
        else:
            data.insert({'user_id': user_id['_id'], 'standard': std, 'grade': grade, 'remark': remark, 'percentage': percentage})
            flash("Record inserted!")
         
    data = mongo.db.records
    results = data.find({'user_id': user_id['_id']})
    
    return render_template("records.html", username=username, standards=int(standards), results = results, error=error)

if __name__ == '__main__':
    app.secret_key = 'ab89559b-8998-4cca-889a-e5b889a9db18'
    app.run(debug=True)

