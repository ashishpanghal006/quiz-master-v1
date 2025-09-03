from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

engine = None
Base = declarative_base()
db = SQLAlchemy()

class User(db.Model):
    __tablename__="user"
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)

class Subject(db.Model):
    __tablename__="subject"
    subject_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    chapters = db.relationship('Chapter', cascade='all, delete',backref='subject')

class Chapter(db.Model):
    __tablename__="chapter"
    chapter_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    subject_id =db.Column(db.Integer, db.ForeignKey("subject.subject_id"), nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    quizzes = db.relationship('Quiz',  cascade='all, delete',backref='chapter')

class Quiz(db.Model):
    __tablename__="quiz"
    quiz_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.chapter_id"), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    questions = db.relationship('Questions', cascade='all, delete',backref='quiz')

class Questions(db.Model):
    __tablename__="questions"
    question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id"), nullable=False)
    question_title = db.Column(db.String, nullable=False)
    question_statement = db.Column(db.String, nullable=False, unique=True)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)

class Scores(db.Model):
    __tablename__="scores"
    score_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    timestamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)