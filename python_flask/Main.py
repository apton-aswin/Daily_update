from datetime import timedelta
from pickle import GET
from flask import Flask, jsonify, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from datetime import datetime
from sqlalchemy import desc
import string
import random


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user1:password@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)
app.config['SECRET_KEY'] = "super secret key"
session_timer = 5
app.permanent_session_lifetime = timedelta(minutes=session_timer)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    mark = db.Column(db.Integer,nullable=False)
    created_at=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, server_default=db.func.now())


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    status = db.Column(db.Integer)
    session_token = db.Column(db.String(80))
    expiration = db.Column(db.String(20))


def session_check():
    user_name = current_user.username
    N = 7
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=N))
    session_token = str(res)
    current_id = current_user.id
    new_session = Sessions(id=current_id, username=user_name,
                           status='1', session_token=session_token, expiration='{} min'.format(session_timer))
    db.session.add(new_session)
    db.session.commit()

@app.route('/')
def home():
    if 'email' in session:
        email = session['email']
        return jsonify({'message': 'You are already logged in', 'email': email})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route('/signup', methods=['POST'])
def signup():
    print('1')

    data = request.json
 # try:
    new_user = User(username=data['name'],
                    password=data['password'], email=data['email'], mark=data['mark'])

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "New user Created"})
    # except:
    #     return jsonify({"message": "Please check your inputs"})


@app.route('/login', methods=["POST"])
def login():

    if "email" in session:
        return redirect("/")
    else:
        _json = request.json
        _email = _json['email']
        _password = _json['password']
        email_signed = []
        password_signed = []
        # validate the received values
        users = User.query.all()
        signed_users = []

        for user in users:
            user_data = {}
            user_data['id'] = user.id
            user_data['name'] = user.username
            user_data['password'] = user.password
            user_data['email'] = user.email
            signed_users.append(user_data)
        for signed_user in signed_users:
            email_signed.append(signed_user['email'])
            password_signed.append(signed_user['password'])
        if _email and _password:

            if(_email in email_signed):

                # if(_password in password_signed):
                email_index = email_signed.index(_email)
                if(_password == password_signed[email_index]):
                    session.permanent = True
                    session["email"] = _email
                    user = User.query.filter_by(email=_email).first()
                    login_user(user)
                    session_check_var = Sessions.query.filter_by(
                        id=current_user.id).first()
                    if(session_check_var):
                        session_check_var.status = "1"
                        db.session.commit()
                    else:
                        session_check()
                    return jsonify({'message': 'Successfully Logged in'})

                else:
                    return jsonify({'message': 'Incorrect Password'})

            else:
                return jsonify({'message': 'Incorrect Email'})
        else:
            return jsonify({"message": "Please enter email and password"})


@app.route("/logout")
@login_required
def logout():
    session_current = Sessions.query.filter_by(
        username=current_user.username).first()
    session_current.status = "0"
    session_current.expiration = "expired"
    db.session.commit()
    logout_user()
    session.pop("email", None)
    return 'You are now logged out!'


@app.route('/home')
@login_required
def currentUser():
    return 'Welcome home {}' .format(current_user.username)


@app.route('/user', methods=['GET'])
@login_required
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.username
        user_data['password'] = user.password
        user_data['email'] = user.email
        output.append(user_data)
    return jsonify({'users': output})

@app.route('/mark', methods=['GET'])
@login_required
def get_all_mark():
    
    users = User.query.order_by(desc(User.mark))
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.username
        user_data['password'] = user.password
        user_data['email'] = user.email
        user_data['mark'] = user.mark
        output.append(user_data)
    return jsonify({'users': output})


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)