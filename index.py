from flask import Flask, render_template, url_for, request, session, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo, pymongo
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField


# import urllib

# db_url = urllib.parse.quote('mongodb://user:user123@ds033499.mongolab.com:33499/enron')

# client = MongoClient(db_url)

app = Flask(__name__)

# app.config['MONGO_DBNAME'] = 'test'
# app.config['MONGO_URI'] = 'mongodb://justincletus:WsP6oB5Fz4CT3L87@cluster0-shard-00-00-steym.gcp.mongodb.net:27017/test'



client = pymongo.MongoClient("mongodb://justincletus:WsP6oB5Fz4CT3L87@cluster0-shard-00-00-steym.gcp.mongodb.net:27017,cluster0-shard-00-01-steym.gcp.mongodb.net:27017,cluster0-shard-00-02-steym.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
mongo = client.test

login_manager = LoginManager()

# mongo = PyMongo(db)

@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})
    print(login_user)

    if login_user:
        if login_user.is_authenticated == True:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        # if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
        #     session['username'] = request.form['username']
        #     return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        students = mongo.db.students
        existing_user = students.find_one({'name': request.form['username']})
        # users = mongo.db.users
        # existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            students.insert({'fullname': request.form['fullname'], 'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = 'ab89559b-8998-4cca-889a-e5b889a9db18'
    app.run(debug=True)
