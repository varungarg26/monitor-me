from flask import Flask, render_template, request, jsonify, make_response, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token
# from flask_mail import Mail, Message
from sqlalchemy import Column, Integer, String, Float, Boolean
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
# import sendgrid
# from sendgrid.helpers.mail import *
import json
import os
# import addon
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
# import requests
from functools import wraps
from flask import Flask, session

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SECRET_KEY'] = 'secret-key'

s = URLSafeTimedSerializer('SECRET_KEY')


db = SQLAlchemy(app)


@app.cli.command('dbCreate')
def db_create():
    db.create_all()
    print('Database created')


@app.cli.command('dbDrop')
def db_drop():
    db.drop_all()
    print('Database Dropped')


@app.cli.command('dbSeed')
def db_seed():
    hashed_password = generate_password_hash('password', method='sha256')
    testUser = User(firstName='User',
                    lastName='Test',
                    email='test@gmail.com',
                    password=hashed_password,
                    public_id=str(uuid.uuid4()))
    db.session.add(testUser)
    db.session.commit()
    print('Seeded')


class User(db.Model):
    id = Column(Integer, primary_key=True)
    public_id = Column(String(50), unique=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    email = Column(String(50), unique=True)
    password = Column(String(50))


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'token' not in session:
            return render_template('need-to-login-error.jinja2')
        else:
            if session is None:
                return render_template('need-to-login-error.jinja2')
            if 'cookie' in request.headers:
                token=session['token']
            if 'cookie' not in request.headers:
                return jsonify(message='Token is missing'),401
            try:
                data=jwt.decode(token, app.config['SECRET_KEY'])
                current_user=User.query.filter_by(public_id=data['public_id']).first()
            except:
                return jsonify(message='Token is invalid'),401

            return f(current_user, *args, **kwargs)
    return decorated


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return 'This is the Sign Up Page'


if __name__ == '__main__':
    app.run(debug=True)
