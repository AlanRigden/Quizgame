import os
import json
import random
import html

from flask import Flask, render_template, request, url_for, redirect, session
import flask_login
from flask_login import UserMixin
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, update

from urllib.request import urlopen

from werkzeug.security import generate_password_hash, check_password_hash

a = generate_password_hash('1234')

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login = LoginManager()
db = SQLAlchemy(app)
app.secret_key = 'xyz'

login.init_app(app)
login.login_view = 'login'


class VideoList(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  urllink = db.Column(db.String(100), nullable=False)
  subject = db.Column(db.String(100), nullable=False)

  def __repr__(self):
    return f'<url {self.urllink}>'


class Users(db.Model, UserMixin):
  Userid = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), nullable=False)
  password_hash = db.Column(db.String(100), nullable=False)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def get_id(self):
    return (self.Userid)


@login.user_loader
def load_user(id):
  return Users.query.get(int(id))

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/about')
def about():
  return render_template('about.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
  if current_user.is_authenticated:
    return redirect('/')
  if request.method == 'POST':
    username = request.form['username']
    user = Users.query.filter_by(username=username).first()
    print(type(user))
    if user is not None and user.check_password(request.form['password']):
      login_user(user)
      return redirect('/')

  return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
  if current_user.is_authenticated:
    return redirect('/')

  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    print(username)
    if Users.query.filter_by(username=username).first():
      print(Users.query.filter_by(username=username))
      return ('Username already Present')

    user = Users(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect('/login')
  return render_template('register.html')


@app.route('/new_vid', methods=('GET', 'POST'))
@login_required
def new_vid():
  if request.method == 'POST':
    urllink = request.form['new_video']
    urllink = urllink.replace('"','')
    subject = request.form['subject']
    new_video = VideoList(urllink=urllink, subject=subject)
    db.session.add(new_video)
    db.session.commit()

    return redirect(url_for('index'))

  return render_template('new_vid.html')


@app.route('/videos')
def videos():
  all_url = VideoList.query.all()
  return render_template('videos.html', all_url=all_url)


@app.route('/blogs')
@login_required
def blog():
  return render_template('blogs.html')


@app.route('/logout')
def logout():
  logout_user()
  return redirect('/')


@app.route('/quiz', methods=['POST', 'GET'])
@login_required
def quizbuilder():
  if request.method == 'POST':
    try:
        cat = request.form['category']
    except:
      cat = 'fault'
    print(cat)
    if cat == 'fault':
        print(cat)
        return render_template('quiz.html')
    else:
      url = 'https://opentdb.com/api.php?amount=10&category=' + cat + '&type=multiple'
      response = urlopen(url)
      data_json = json.loads(response.read())
      questions = []
      all_answers = []
      c_answers = []
      data_sent = data_json['results']

      single = data_sent[0]
      subject = single['category']
      for question in data_sent:
        answers = []
        qtext = question['question']
        #print(qtext)
        questions.append(qtext)
        correct_a = html.unescape(question['correct_answer'])
        c_answers.append(correct_a)
        answers.append(correct_a)
        incorrect_a = question['incorrect_answers']
        for answer in incorrect_a:
          answers.append(html.unescape(answer))
        random.shuffle(answers)
        all_answers.append(answers)
        #print(answers)

      session['answers'] = c_answers
      return render_template('quiz.html',
                             subject=subject,
                             data_json=data_json,
                             questions=questions,
                             answers=all_answers,
                             c_answers=c_answers,
                             showButton="block")
  else:
    return render_template('quiz.html', showButton="none")


@app.route('/mark', methods=['POST', 'GET'])
@login_required
def mark():
  quest = []
  total = 0
  correct = 0
  questions = request.form
  questions = questions.to_dict(flat=True)
  answers = session.get('answers', None)
  #print(questions)
  for que in questions.values():
    quest.append(que)
    #print(que)
    #print(answers[total])
    if que == answers[total]:
      correct += 1
    total += 1

  return render_template('mark.html',
                         questions=quest,
                         answers=answers,
                         total=total,
                         correct=correct)


app.run(host='0.0.0.0', port=8080, debug=True)
