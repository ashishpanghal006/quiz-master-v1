from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template,  request, url_for, redirect, session
from datetime import datetime, timedelta
from flask import current_app as app
from werkzeug.utils import secure_filename
from .models import *
import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
from sqlalchemy.sql import func
from collections import defaultdict
import os


#home route.............................................................................................
@app.route("/", methods=["GET"])
def home():
    return render_template("login.html")

# login route.................................................................................................
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("password")

        usr = User.query.filter_by(email = email, password = pwd).first()
        if email == "admin@gmail.com" and pwd == "admin123":
            return redirect(url_for("admin_dashboard", email="admin@gmail.com"))
        elif usr:
            return redirect(url_for("user_dashboard",email=email, user_id=usr.user_id))
        else:
            return render_template("login.html", msg="Invalid credentials!")
    return render_template("login.html", msg="")


# user registeration................................................................................
@app.route("/user_reg_page", methods=["GET"])
def signup_user():
    return render_template("user_registeration.html")

@app.route("/user_register", methods=["GET", "POST"])
def register_user():
    if request.method=="POST":
        email = request.form.get("email")
        fullname = request.form.get("fullname")
        pwd = request.form.get("password")
        qualification = request.form.get("qualification")
        dob = request.form.get("dob")

        usr = User.query.filter_by(email = email).first()
        if usr:
            return render_template("user_registeration.html", msg="Sorry , this email already registered")
        elif email=="":
            return render_template("user_registeration.html", msg="please fill all the fields")
        elif fullname=="":
            return render_template("user_registeration.html", msg="please fill all the fields")
        elif dob=="":
            return render_template("user_registeration.html", msg="please fill all the fields")
        elif pwd=="":
            return render_template("user_registeration.html", msg="please fill all the fields")
        elif qualification=="":
            return render_template("user_registeration.html", msg="please fill all the fields")
        new_user = User(email=email, fullname=fullname, password=pwd, qualification=qualification, dob=dob)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("home", msg="Registeration Succeessful"))
    return render_template("user_registeration.html", msg="")


#common route for admin and user dashboard.........................................................................
@app.route("/admin/<email>")
def admin_dashboard(email):
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quiz = Quiz.query.all()
    return render_template("admin_dashboard.html", email=email, subjects=subjects, chapters=chapters, quiz=quiz)

@app.route("/user/<user_id>/<email>")
def user_dashboard(user_id,email):
    today = datetime.today().date()
    quizzes = Quiz.query.filter(Quiz.date_of_quiz > today).order_by(Quiz.date_of_quiz).all()
    questions = Questions.query.all()
    return render_template("user_dashboard.html",email=email, user_id=user_id, quizzes=quizzes, questions=questions)

# route for quiz under admin..................................
@app.route("/quiz_admin/<email>", methods=["GET", "POST"])
def quiz_admin(email):
    quizes = Quiz.query.all()
    chapters = Chapter.query.all()
    questions = Questions.query.all()
    return render_template("quiz_admin.html", email=email, quizes=quizes, chapters=chapters, questions=questions)

#route for scores under user dashboard.......................................
@app.route("/scores/<user_id>/<email>", methods=["GET", "POST"])
def scores(user_id, email):
    user_scores = (
        db.session.query(Scores, Chapter.name.label("chapter_name"), db.func.count(Questions.question_id).label("num_questions"))
        .join(Quiz, Scores.quiz_id == Quiz.quiz_id)
        .join(Chapter, Quiz.chapter_id == Chapter.chapter_id)
        .join(Questions, Quiz.quiz_id == Questions.quiz_id)
        .filter(Scores.user_id == user_id)
        .group_by(Scores.score_id, Chapter.name, Scores.timestamp_of_attempt)
        .order_by(Scores.timestamp_of_attempt.desc())
        .all()
    )
    return render_template("scores.html", scores=user_scores, email=email, user_id=user_id)

#many controllers/routers here.....
# add , delete and edit subject routes.......................................................................................
@app.route("/add_subject/<email>", methods=["GET", "POST"])
def add_subject(email):
    if request.method=="POST":
        name = request.form.get("name")
        description = request.form.get("description")
        
        sub = Subject.query.filter_by(name=name).first()
        if sub:
            return render_template("add_subject.html",email=email, msg="subject already exist")
        elif name=="":
            return render_template("add_subject.html",email=email, msg="enter the subject name")
        elif description=="":
            return render_template("add_subject.html",email=email, msg="enter the description")
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for("admin_dashboard", email="admin@gmail.com"))
    return render_template("add_subject.html",email=email, msg="")


@app.route("/delete_subject/<subject_id>/<email>", methods=["GET", "POST"])
def delete_subject(subject_id, email):
    subject = Subject.query.filter_by(subject_id=subject_id).first()
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for("admin_dashboard", email=email))


@app.route("/edit_subject/<subject_id>/<email>", methods=["GET", "POST"])
def edit_subject(subject_id, email):
    subject = Subject.query.filter_by(subject_id=subject_id).first()
    if request.method=="POST":
        name = request.form.get("name")
        description = request.form.get("description")

        subject.name = name
        subject.description = description
        db.session.commit()
        return redirect(url_for("admin_dashboard", email=email))
    return render_template("edit_subject.html", subject=subject, email=email)


# add, delete and edit chapter routes.....................................................................................
@app.route("/add_chapter/<subject_id>/<email>", methods=["GET", "POST"])
def add_chapter(subject_id, email):
    if request.method=="POST":
        name = request.form.get("name")
        description = request.form.get("description")

        chapter = Chapter.query.filter_by(name=name).first()
        if chapter:
            return render_template("add_chapter.html",email=email, msg="chapter already exist")
        elif name=="":
            return render_template("add_chapter.html",email=email, msg="enter the subject name")
        elif description=="":
            return render_template("add_chapter.html",email=email, msg="enter the description")
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for("admin_dashboard", email="admin@gmail.com"))
    return render_template("add_chapter.html",email=email, subject_id=subject_id, msg="")


@app.route("/delete_chapter/<chapter_id>/<email>", methods=["GET", "POST"])
def delete_chapter(chapter_id, email):
    chapter = Chapter.query.filter_by(chapter_id=chapter_id).first()
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for("admin_dashboard", email=email))


@app.route("/edit_chapter/<subject_id>/<chapter_id>/<email>", methods=["GET", "POST"])
def edit_chapter(subject_id,chapter_id, email):
    chapter = Chapter.query.filter_by(chapter_id=chapter_id).first()
    if request.method=="POST":
        name = request.form.get("name")
        description = request.form.get("description")

        chapter.name = name
        chapter.description = description
        db.session.commit()
        return redirect(url_for("admin_dashboard", email=email))
    return render_template("edit_chapter.html", chapter=chapter, email=email, subject_id=subject_id)


# add, delete and edit routes for quiz.......................................................
@app.route("/add_quiz/<email>", methods=["GET", "POST"])
def add_quiz(email):
    chapters = Chapter.query.all() 
    if request.method=="POST":
        chapter_id = request.form.get("chapter_id")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")
        date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        time_duration = datetime.strptime(time_duration, "%H:%M").time()

        quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()
        if quiz:
            return render_template("add_quiz.html", email=email, chapters=chapters, msg="quiz for this chapter already exist")
        elif ((time_duration) or (date_of_quiz))=="":
            return render_template("add_quiz.html", email=email, chapters=chapters, msg="please fill all fields")
        new_quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration)
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for("quiz_admin", email=email))
    return render_template("add_quiz.html", email=email, chapters=chapters, msg="")


@app.route("/edit_quiz/<quiz_id>/<email>", methods=["GET", "POST"])
def edit_quiz(quiz_id, email):
    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if request.method=="POST":
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")
        date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        time_duration = datetime.strptime(time_duration, "%H:%M:%S").time()

        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = time_duration
        db.session.commit()
        return redirect(url_for("quiz_admin", email=email))
    return render_template("edit_quiz.html", quiz=quiz,email=email)


@app.route("/delete_quiz/<quiz_id>/<email>", methods=["GET", "POST"])
def delete_quiz(quiz_id, email):
    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for("quiz_admin", email=email))


# add, delete and edit route for questions.................................................................
@app.route("/add_question/<quiz_id>/<email>", methods=["GET", "POST"])
def add_question(quiz_id, email):
    if request.method=="POST":
        question_title = request.form.get("question_title")
        question_statement = request.form.get("question_statement")
        quiz_id = request.form.get("quiz_id")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        answer = request.form.get("answer")

        question = Questions.query.filter_by(question_statement=question_statement).first()
        if question:
            return render_template("add_question.html",email=email, quiz_id=quiz_id, msg="question already exist")
        elif ((question_title)or (question_statement)or (option1)or (option2)or (option3)or (option4)or (answer))=="":
            return render_template("add_question.html",email=email, quiz_id=quiz_id, msg="enter all fields")
        new_question = Questions(question_title=question_title, question_statement=question_statement, quiz_id=quiz_id, option1=option1, option2=option2, option3=option3, option4=option4, answer=answer)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("add_question", email=email, quiz_id=quiz_id, msg=""))
    return render_template("add_question.html",email=email, quiz_id=quiz_id, msg="")


@app.route("/edit_question/<question_id>/<email>", methods=["GET", "POST"])
def edit_question(question_id, email):
    question = Questions.query.filter_by(question_id=question_id).first()
    if request.method=="POST":
        question_title = request.form.get("question_title")
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        answer = request.form.get("answer")

        question.question_title = question_title
        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.answer = answer
        db.session.commit()
        return redirect(url_for("quiz_admin", email=email))
    return render_template("edit_question.html", question=question, email=email)


@app.route("/delete_question/<question_id>/<email>", methods=["GET", "POST"])
def delete_question(question_id, email):
    question = Questions.query.filter_by(question_id=question_id).first()
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("quiz_admin", email=email))


# route for viewing quiz details.................................................................
@app.route("/view_quiz/<quiz_id>/<chapter_id>/<user_id>/<email>", methods=["GET", "POST"])
def view_quiz(quiz_id, user_id, chapter_id, email):
    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    questions = Questions.query.filter_by(quiz_id=quiz_id).count()
    chapter = Chapter.query.filter_by(chapter_id=chapter_id).first()
    subject = Subject.query.all()
    return render_template("view_quiz.html", email=email, user_id=user_id, quiz=quiz, questions=questions, chapter=chapter, subject=subject)


# route for starting the quiz..............................................................................................
@app.route('/start_quiz/<quiz_id>/<user_id>/<email>', methods=['GET', 'POST'])
def start_quiz(quiz_id, user_id, email):
    quiz = Quiz.query.get(quiz_id)
    questions = Questions.query.filter_by(quiz_id=quiz_id).all()
    
    total_seconds = quiz.time_duration.hour * 3600 + quiz.time_duration.minute * 60 + quiz.time_duration.second
    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.question_id}')

            if user_answer == question.answer:
                score += 1
        
        new_score = Scores(
            quiz_id=quiz_id,
            user_id=user_id,
            timestamp_of_attempt=datetime.utcnow(),
            total_scored=score
        )
        db.session.add(new_score)
        db.session.commit()
        return redirect(url_for("user_dashboard", email=email, user_id=user_id))
    
    return render_template('start_quiz.html', quiz=quiz, questions=questions, time_limit=total_seconds, quiz_id=quiz_id,email=email, user_id=user_id)


# route for search operation by admin..................................................................................
@app.route("/search_subject_for_admin/<email>", methods=["GET", "POST"])
def search_subject(email):
    if request.method == "POST":
        search_txt = request.form.get("search_txt")
        by_subject = Subject.query.filter(Subject.name.like(f"%{search_txt}%"))
        if by_subject:
            chapters = Chapter.query.all()
            quiz = Quiz.query.all()
            return render_template("admin_dashboard.html", email=email, subjects=by_subject, chapters=chapters, quiz=quiz)
        else:
            return render_template("admin_dashboard.html", email=email)
    return redirect(url_for("admin_dashboard", email=email))


@app.route("/search_quiz_for_admin/<email>", methods=["GET", "POST"])
def search_quiz_as_admin(email):
    if request.method == "POST":
        search_txt = request.form.get("search_txt")

        by_subject = Quiz.query.join(Chapter).join(Subject).filter(Subject.name.like(f"%{search_txt}%")).all()
        by_chapter = Quiz.query.join(Chapter).filter(Chapter.name.like(f"%{search_txt}%")).all()
        chapters = Chapter.query.all()
        questions = Questions.query.all()
        if by_subject:
            return render_template("quiz_admin.html", email=email, quizes=by_subject, chapters=chapters, questions=questions)
        elif by_chapter:
            return render_template("quiz_admin.html", email=email, quizes=by_chapter, chapters=chapters, questions=questions)
        else:
            return render_template("quiz_admin.html", email=email)  
    return redirect(url_for("quiz_admin"), email=email)


# route for search operation by user.........................................................................
@app.route("/search_quiz_for_user/<user_id>/<email>", methods=["GET", "POST"])
def search_quiz_as_user(user_id, email):
    if request.method == "POST":
        search_txt = request.form.get("search_txt")
        by_date = sorted(Quiz.query.filter(Quiz.date_of_quiz.like(f"%{search_txt}%")).all(), key=lambda x: x.date_of_quiz)
        questions = Questions.query.all()
        by_subject = Quiz.query.join(Chapter).join(Subject).filter(Subject.name.like(f"%{search_txt}%")).all()

        if by_date:
            return render_template("user_dashboard.html",email=email, user_id=user_id, quizzes=by_date, questions=questions)
        elif by_subject:
            return render_template("user_dashboard.html",email=email, user_id=user_id, quizzes=by_subject, questions=questions)
        else:
            return render_template("user_dashboard.html",email=email, user_id=user_id)        
    return redirect(url_for("user_dashboard",email=email, user_id=user_id))

@app.route("/search_score_for_user/<user_id>/<email>", methods=["GET", "POST"])
def search_scores(user_id, email):
    if request.method == "POST":
        search_txt = request.form.get("search_txt")

        user_scores = (
            db.session.query(Scores, Chapter.name.label("chapter_name"), db.func.count(Questions.question_id).label("num_questions"))
            .join(Quiz, Scores.quiz_id == Quiz.quiz_id)
            .join(Chapter, Quiz.chapter_id == Chapter.chapter_id)
            .join(Questions, Quiz.quiz_id == Questions.quiz_id)
            .filter(Scores.user_id == user_id, Chapter.name.ilike(f"%{search_txt}%"))  # Search by chapter name (case-insensitive)
            .group_by(Scores.score_id, Chapter.name, Scores.timestamp_of_attempt)
            .all()
        )
        return render_template("scores.html", scores=user_scores, email=email, user_id=user_id)
    return render_template("scores.html", scores=[], email=email, user_id=user_id)


# route for user summary..........................................................................................
@app.route("/user_summary/<user_id>/<email>")
def user_summary(user_id,email):
    summary_data = db.session.query(
        Chapter.name.label('chapter_name'),
        func.count(Scores.score_id).label('num_attempts'),
        func.avg(Scores.total_scored).label('avg_score'),
        func.max(Scores.total_scored).label('best_score')
    ).join(Quiz, Quiz.chapter_id == Chapter.chapter_id) \
     .join(Scores, Scores.quiz_id == Quiz.quiz_id) \
     .filter(Scores.user_id == user_id) \
     .group_by(Chapter.name) \
     .all()

    return render_template("user_summary.html", user_id=user_id, email=email, summary_data=summary_data)
    

# route for admin summary.........................................................................................
@app.route("/admin_summary/<email>")
def admin_summary(email):
    users = User.query.filter(User.email != email).all()
    user_data = []
    for user in users:
        quiz_attempts = Scores.query.filter_by(user_id=user.user_id).count()
        user_data.append({'fullname': user.fullname, 'email': user.email, 'quizzes_attempted': quiz_attempts})
    
    subjects = Subject.query.all()
    subject_names = []
    quiz_counts = []
    for subject in subjects:
        total_quizzes = sum(len(chapter.quizzes) for chapter in subject.chapters)
        subject_names.append(subject.name)
        quiz_counts.append(total_quizzes)
    
    plt.figure(figsize=(8, 5))
    plt.bar(subject_names, quiz_counts, color='skyblue')
    plt.xlabel('Subjects')
    plt.ylabel('No. of Quizzes')
    plt.title('Quizzes per Subject')
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = os.path.join(app.root_path, 'static', 'subject_quiz_bar.png')
    plt.savefig(chart_path)
    plt.close()
    
    return render_template('admin_summary.html', email=email, user_data=user_data, chart_path='/static/subject_quiz_bar.png')