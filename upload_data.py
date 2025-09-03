from application.models import *
from application.models import db

def upload_data():
    from flask import current_app
    with current_app.app_context():
        admin = User(
            email='admin@gmail.com',
            password='admin123',
            fullname='Admin',
            qualification='None',
            dob='12-06-1996'
        )
        user1 = User(
            email="ashish@gmail.com",
            password = "ashish",
            fullname = "ashish",
            qualification="12th",
            dob='12-06-2004'
        )
        user2 = User(
            email="hitesh@gmail.com",
            password = "hitesh",
            fullname = "hitesh",
            qualification="12th",
            dob='20-06-2004'
        )
        subject1 = Subject(
            name = "App Dev 1",
            description = "learning the basics of application development"
        )
        subject2 = Subject(
            name = "Physics",
            description = "learn the various concepts of physics"
        )
        subject3 = Subject(
            name = "English",
            description = "grace your english knowledge"
        )
        chapter1 = Chapter(
            subject_id = 1,
            name = "HTML",
            description = "learn html"
        )
        chapter2 = Chapter(
            subject_id = 1,
            name = "CSS",
            description = "learn css"
        )
        chapter3 = Chapter(
            subject_id = 3,
            name = "preposition",
            description = "explore preposition"
        )
        quiz1 = Quiz(
            chapter_id = 3,
            date_of_quiz = datetime.strptime("2025-05-15", "%Y-%m-%d").date(),
            time_duration = datetime.strptime("00:20", "%H:%M").time()
        )
        question1 = Questions(
            quiz_id = 1,
            question_title = "on",
            question_statement = "She is sitting ____ the chair.",
            option1 = "on",
            option2 = "in",
            option3 = "at",
            option4 = "up",
            answer = "on"
        )
        question2 = Questions(
            quiz_id = 1,
            question_title = "on",
            question_statement = "The book is ____ the table.",
            option1 = "on",
            option2 = "in",
            option3 = "at",
            option4 = "up",
            answer = "on"
        )
        question3 = Questions(
            quiz_id = 1,
            question_title = "in",
            question_statement = "He was born __ 1995.",
            option1 = "on",
            option2 = "in",
            option3 = "at",
            option4 = "up",
            answer = "in"
        )
        question4 = Questions(
            quiz_id = 1,
            question_title = "at",
            question_statement = "The train arrives ____ 5 pm.",
            option1 = "on",
            option2 = "in",
            option3 = "at",
            option4 = "up",
            answer = "at"
        )
        question5 = Questions(
            quiz_id = 1,
            question_title = "in",
            question_statement = "i live ___ New York.",
            option1 = "on",
            option2 = "in",
            option3 = "at",
            option4 = "up",
            answer = "in"
        )
        db.session.add_all([admin, user1, user2])
        db.session.add_all([subject1, subject2, subject3])
        db.session.add_all([chapter1, chapter2, chapter3])
        db.session.add(quiz1)
        db.session.add_all([question1, question2, question3, question4, question5])
        db.session.commit()