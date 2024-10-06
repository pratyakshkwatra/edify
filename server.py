from flask import Flask, render_template, request, jsonify, redirect
from flask import session as flask_session
from sqlalchemy.orm import sessionmaker
import database as db
import functions
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import concurrent.futures
import mdtex2html
import favicon

app = Flask(__name__)
app.secret_key = "some_random_super_secret_key_that_no_one_knows_according_to_us_but_they_probably_do"

now = datetime.now()

def get_day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

@app.route("/")
@app.route("/home")
def base():
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            Session = sessionmaker(bind=db.engine)
            session = Session()

            created_tests_rec: list[db.Onboarding] = (
                session.query(db.Onboarding)
                .filter(db.Onboarding.user_id == flask_session["userID"])
                .all()
            )
            created_tests = []

            for test in created_tests_rec:
                allow_generate = False
                question_count = 0

                chapters: list[db.Chapter] = (
                    session.query(db.Chapter)
                    .filter(db.Chapter.onboarding_id == test.id)
                    .all()
                )
                for chapter in chapters:
                    topics: list[db.Topic] = (
                        session.query(db.Topic)
                        .filter(db.Topic.chapter_id == chapter.id)
                        .all()
                    )

                    for topic in topics:
                        questions = (
                            session.query(db.Question)
                            .filter(db.Question.topic_id == topic.id)
                            .all()
                        )
                        for question in questions:
                            answer = (
                                session.query(db.Answer)
                                .filter(db.Answer.question_id == question.id)
                                .first()
                            )
                            if answer != None:
                                allow_generate = True
                        question_count += len(questions)

                created_tests.append(
                    {
                        "title": f"{test.grade_year} - {test.subject}",
                        "timestamp": test.timestamp,
                        "question_count": question_count,
                        "score": test.score,
                        "id": test.id,
                        "type": (
                            2
                            if test.report_generated
                            else 1 if allow_generate else 0
                        ),
                    }
                )
            
            strengths = []
            weaknesses = []

            Session = sessionmaker(bind=db.engine)
            session = Session()
            
            created_tests_rec: list[db.Onboarding] = (
                session.query(db.Onboarding)
                .filter(db.Onboarding.user_id == flask_session["userID"])
                .all()
            )

            for test in created_tests_rec:
                chapters: list[db.Chapter] = (
                    session.query(db.Chapter)
                    .filter(db.Chapter.onboarding_id == test.id)
                    .all()
                )
                for chapter in chapters:
                    topics: list[db.Topic] = (
                        session.query(db.Topic)
                        .filter(db.Topic.chapter_id == chapter.id)
                        .all()
                    )

                    for topic in topics:
                        if topic.score < 0.75:
                            weaknesses.append(topic.title)
                        else:
                            strengths.append(topic.title)

            return render_template(
                "index.html",
                test_count=len(created_tests),
                weak_count=len(weaknesses),
                strength_count=len(strengths),
                created_tests=reversed(created_tests),
            )
        else:
            return redirect("/login")
    else:
        return redirect("/login")


@app.route("/logout")
def logout():
    flask_session["loggedIn"] = False
    flask_session["userID"] = None
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=request.args.get("error"))
    else:
        username = str(request.form.get("username"))
        password = str(request.form.get("password"))

        Session = sessionmaker(bind=db.engine)
        session = Session()

        student = (
            session.query(db.User).filter(db.User.username == username).first()
        )

        if student == None:
            return redirect("/login?error=Account doesn't exist")

        if not check_password_hash(student.password, password):
            return redirect("/login?error=Invalid username/password")

        flask_session["loggedIn"] = True
        flask_session["userID"] = student.id

        return redirect("/home")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", error=request.args.get("error"))
    else:
        username = request.form.get("username")
        password = str(request.form.get("password"))

        Session = sessionmaker(bind=db.engine)
        session = Session()

        if (
            session.query(db.User).filter(db.User.username == username).first()
            != None
        ):
            return redirect("/signup?error=Username already exists")

        hashed_pass = generate_password_hash(password)

        new_user = db.User(username=username, password=hashed_pass)

        session.add(new_user)
        session.commit()

        session.refresh(new_user)
        flask_session["loggedIn"] = True
        flask_session["userID"] = new_user.id

        session.close()
        return redirect("/home")


@app.route("/create", methods=["GET", "POST"])
def create():
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            if request.method == "GET":
                return render_template("create.html")
            else:
                data = {
                    "grade_year": request.form.get("grade_year"),
                    "goal": request.form.get("goal"),
                    "subject": request.form.get("subject"),
                    "chapters": request.form.get("chapters").split(","),
                }

                Session = sessionmaker(bind=db.engine)
                session = Session()

                new_onboarding = db.Onboarding(
                    user_id=flask_session["userID"],
                    grade_year=data["grade_year"],
                    goal=data["goal"],
                    subject=data["subject"],
                    score=0,
                    timestamp=now.strftime(
                        f"%-d{get_day_suffix(now.day)} %B, %Y at %H:%M HR"
                    ),
                )
                session.add(new_onboarding)
                session.commit()
                session.refresh(new_onboarding)

                for chapter in data["chapters"]:
                    final_chapter = str(chapter).strip()
                    new_chapter = db.Chapter(
                        onboarding_id=new_onboarding.id, title=final_chapter
                    )
                    session.add(new_chapter)
                    session.commit()

                    session.refresh(new_chapter)

                    topics = functions.getTopicsFromChapter(
                        final_chapter,
                        data["subject"],
                        data["grade_year"],
                        data["goal"],
                    )

                    for topic in topics:
                        final_topic = str(topic).strip()
                        new_topic = db.Topic(
                            chapter_id=new_chapter.id,
                            title=final_topic,
                            score=0,
                        )
                        session.add(new_topic)
                        session.commit()

                onboarding_id = new_onboarding.id

                session.close()

                return redirect(f"/onboarding_confirmation/{onboarding_id}")
        else:
            return redirect("/login")
    else:
        return redirect("/login")


@app.route("/onboarding_confirmation/<int:test_id>")
def onboarding_confirmation(test_id: int):
    return render_template("are_you_ready.html", test_id=test_id)


@app.route("/onboarding_test/<int:test_id>", methods=["GET", "POST"])
def onboarding_test(test_id: int):
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            if request.method == "GET":
                return render_template("create.html")
            else:
                question_list: list = []

                Session = sessionmaker(bind=db.engine)
                session = Session()

                questions_exist = False
                chapters: list[db.Chapter] = (
                    session.query(db.Chapter)
                    .filter(db.Chapter.onboarding_id == test_id)
                    .all()
                )
                for chapter in chapters:
                    topics: list[db.Topic] = (
                        session.query(db.Topic)
                        .filter(db.Topic.chapter_id == chapter.id)
                        .all()
                    )

                    for topic in topics:
                        questions_exist = (
                            True
                            if session.query(db.Question)
                            .filter(db.Question.topic_id == topic.id)
                            .first()
                            != None
                            else False
                        )

                if questions_exist:
                    chapters: list[db.Chapter] = (
                        session.query(db.Chapter)
                        .filter(db.Chapter.onboarding_id == test_id)
                        .all()
                    )
                    for chapter in chapters:
                        topics: list[db.Topic] = (
                            session.query(db.Topic)
                            .filter(db.Topic.chapter_id == chapter.id)
                            .all()
                        )

                        for topic in topics:
                            questions = (
                                session.query(db.Question)
                                .filter(db.Question.topic_id == topic.id)
                                .all()
                            )

                            for question in questions:
                                question_list.append(
                                    {
                                        "question": question.question_body,
                                        "option1": question.option1,
                                        "option2": question.option2,
                                        "option3": question.option3,
                                        "option4": question.option4,
                                    }
                                )
                else:

                    def process_topic(
                        topic, chapter, onboarding_test, question_list, session
                    ):

                        new_questions = functions.getMCQQuestions(
                            topic.title,
                            chapter.title,
                            onboarding_test.grade_year,
                            onboarding_test.goal,
                        )

                        for question in new_questions:
                            new_ques = db.Question(
                                topic_id=topic.id,
                                question_body=question["question"],
                                option1=question["option1"],
                                option2=question["option2"],
                                option3=question["option3"],
                                option4=question["option4"],
                            )
                            session.add(new_ques)

                        session.commit()

                    def process_chapter(
                        chapter, onboarding_test, question_list, session
                    ):

                        topics = (
                            session.query(db.Topic)
                            .filter(db.Topic.chapter_id == chapter.id)
                            .all()
                        )

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            futures = [
                                executor.submit(
                                    process_topic,
                                    topic,
                                    chapter,
                                    onboarding_test,
                                    question_list,
                                    session,
                                )
                                for topic in topics
                            ]

                            concurrent.futures.wait(futures)

                    onboarding_test = (
                        session.query(db.Onboarding)
                        .filter(db.Onboarding.id == test_id)
                        .first()
                    )

                    chapters = (
                        session.query(db.Chapter)
                        .filter(db.Chapter.onboarding_id == test_id)
                        .all()
                    )

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = [
                            executor.submit(
                                process_chapter,
                                chapter,
                                onboarding_test,
                                question_list,
                                session,
                            )
                            for chapter in chapters
                        ]

                        concurrent.futures.wait(futures)
                    
                    chapters: list[db.Chapter] = (
                        session.query(db.Chapter)
                        .filter(db.Chapter.onboarding_id == test_id)
                        .all()
                    )
                    for chapter in chapters:
                        topics: list[db.Topic] = (
                            session.query(db.Topic)
                            .filter(db.Topic.chapter_id == chapter.id)
                            .all()
                        )

                        for topic in topics:
                            questions = (
                                session.query(db.Question)
                                .filter(db.Question.topic_id == topic.id)
                                .all()
                            )

                            for question in questions:
                                question_list.append(
                                    {
                                        "question": question.question_body,
                                        "option1": question.option1,
                                        "option2": question.option2,
                                        "option3": question.option3,
                                        "option4": question.option4,
                                    }
                                )

                session.close()

                return render_template(
                    "onboarding_test.html",
                    question_list=question_list,
                    test_id=test_id,
                )
        else:
            return redirect("/login")
    else:
        return redirect("/login")


@app.route("/onboarding_submit/<int:test_id>", methods=["POST"])
def onboarding_submit(test_id: int):
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            if request.method == "GET":
                return render_template("create.html")
            else:
                data = request.form.to_dict()
                question_list: list = []

                Session = sessionmaker(bind=db.engine)
                session = Session()

                chapters: list[db.Chapter] = (
                    session.query(db.Chapter)
                    .filter(db.Chapter.onboarding_id == test_id)
                    .all()
                )
                for chapter in chapters:
                    topics: list[db.Topic] = (
                        session.query(db.Topic)
                        .filter(db.Topic.chapter_id == chapter.id)
                        .all()
                    )

                    for topic in topics:
                        questions = (
                            session.query(db.Question)
                            .filter(db.Question.topic_id == topic.id)
                            .all()
                        )

                        for question in questions:
                            question_list.append(
                                {
                                    "question": question.question_body,
                                    "option1": question.option1,
                                    "option2": question.option2,
                                    "option3": question.option3,
                                    "option4": question.option4,
                                    "id": question.id,
                                }
                            )

                for question in question_list:
                    index = question_list.index(question) + 1
                    if str(index) in data:
                        new_answer = db.Answer(
                            question_id=question["id"],
                            answer_option=data[str(index)],
                            score=0,
                        )
                        session.add(new_answer)
                        session.commit()
                    else:
                        new_answer = db.Answer(
                            question_id=question["id"], answer_option=0, score=0
                        )
                        session.add(new_answer)
                        session.commit()

                session.close()

                return render_template("generate_result.html", test_id=test_id)
        else:
            return redirect("/login")
    else:
        return redirect("/login")


@app.route("/generate_result/<int:test_id>", methods=["GET", "POST"])
def generate_result(test_id: int):
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            if request.method == "GET":
                return render_template("generate_result.html", test_id=test_id)
            else:
                Session = sessionmaker(bind=db.engine)
                session = Session()

                onboarding_test = (
                    session.query(db.Onboarding)
                    .filter(db.Onboarding.id == test_id)
                    .first()
                )
                onboarding_test.score = 0
                session.commit()
                session.refresh(onboarding_test)

                chapters: list[db.Chapter] = (
                    session.query(db.Chapter)
                    .filter(db.Chapter.onboarding_id == test_id)
                    .all()
                )
                for chapter in chapters:
                    topics: list[db.Topic] = (
                        session.query(db.Topic)
                        .filter(db.Topic.chapter_id == chapter.id)
                        .all()
                    )

                    for topic in topics:
                        data_send = []

                        questions = (
                            session.query(db.Question)
                            .filter(db.Question.topic_id == topic.id)
                            .all()
                        )

                        total_ques = len(questions)
                        correct_ques = 0

                        for question in questions:
                            answer = (
                                session.query(db.Answer)
                                .filter(db.Answer.question_id == question.id)
                                .first()
                            )
                            if answer.answer_option != 0:
                                data_send.append(
                                    {
                                        "question": question.question_body,
                                        "option1": question.option1,
                                        "option2": question.option2,
                                        "option3": question.option3,
                                        "option4": question.option4,
                                        "answer": f"option {answer.answer_option}",
                                    }
                                )

                        if data_send != []:
                            scores = functions.check_answer_per_topic(
                                data_send,
                                topic.title,
                                chapter.title,
                                onboarding_test.grade_year,
                                onboarding_test.subject,
                            )
                            
                            count = 0

                            for question in questions:
                                answer = (
                                    session.query(db.Answer)
                                    .filter(db.Answer.question_id == question.id)
                                    .first()
                                )
                                if answer.answer_option != 0:
                                    answer.score = scores[count]
                                    if scores[count] == 1:
                                        correct_ques += 1
                                    onboarding_test.score += scores[
                                        count
                                    ]
                                    session.commit()
                                    count += 1

                        topic.score = correct_ques / total_ques
                        session.commit()

                onboarding_test.report_generated = True
                session.commit()

                session.close()

                return redirect("/home")
        else:
            return redirect("/login")
    else:
        return redirect("/login")


@app.route("/view_report/<int:test_id>", methods=["GET"])
def view_report(test_id: int):
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            if request.method == "GET":
                data_list = []
                strengths = []
                weaknesses = []

                Session = sessionmaker(bind=db.engine)
                session = Session()

                chapters: list[db.Chapter] = (
                    session.query(db.Chapter)
                    .filter(db.Chapter.onboarding_id == test_id)
                    .all()
                )
                for chapter in chapters:
                    topics: list[db.Topic] = (
                        session.query(db.Topic)
                        .filter(db.Topic.chapter_id == chapter.id)
                        .all()
                    )

                    for topic in topics:
                        if topic.score < 0.75:
                            weaknesses.append({'title': topic.title, "id": topic.id})
                        else:
                            strengths.append(topic.title)

                        questions = (
                            session.query(db.Question)
                            .filter(db.Question.topic_id == topic.id)
                            .all()
                        )

                        for question in questions:
                            answer = (
                                session.query(db.Answer)
                                .filter(db.Answer.question_id == question.id)
                                .first()
                            )
                            data_list.append(
                                {
                                    "question": question.question_body,
                                    "user_answer": (
                                        question.option1
                                        if answer.answer_option == 1
                                        else (
                                            question.option2
                                            if answer.answer_option == 2
                                            else (
                                                question.option3
                                                if answer.answer_option == 3
                                                else question.option4 if answer.answer_option == 4 else "Not Attempted"
                                            )
                                        )
                                    ),
                                    "score": answer.score,
                                }
                            )

                return render_template(
                    "view_report.html",
                    data_list=data_list,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    test_id=test_id
                )
        else:
            return redirect("/login")
    else:
        return redirect("/login")
    
@app.route("/lets_improve/<int:test_id>/<int:weakness>", methods=["POST"])
def lets_improve(test_id: int, weakness: int):
    if "loggedIn" in flask_session:
        if flask_session["loggedIn"] == True:
            if request.method == "POST":
                Session = sessionmaker(bind=db.engine)
                session = Session()
                
                onboarding_test = session.query(db.Onboarding).filter(db.Onboarding.id == test_id).first()
                topic_db = session.query(db.Topic).filter(db.Topic.id == weakness).first()
                
                notes_db = session.query(db.Notes).filter(db.Notes.topic_id == topic_db.id).first()
                
                if notes_db != None:
                    notes = notes_db.content
                    topic = notes_db.topic_full
                else:
                    notes = functions.generate_notes(topic_db.title, onboarding_test.grade_year, onboarding_test.goal)
                
                    topic = f"{onboarding_test.grade_year}: {topic_db.title}"
                    
                    new_notes = db.Notes(topic_id=topic_db.id, content=notes, topic_full=topic)
                    session.add(new_notes)
                    session.commit()
                
                session.close()
                
                notes_final = mdtex2html.convert(
                    notes
                )
                
                top_searches = functions.get_top_search_results(topic)
                
                icons = []
                titles = []
                
                for search in top_searches:
                    try:
                        icon: favicon.Icon = favicon.get(search)[0]
                        icons.append(icon.url)
                    except:
                        pass
                    titles.append(functions.get_main_domain(search))
                                                        
                return render_template(
                    "lets_improve.html",
                    notes=notes_final,
                    topic=topic,
                    top_searches=top_searches,
                    icons=icons,
                    titles=titles,
                )
        else:
            return redirect("/login")
    else:
        return redirect("/login")


if __name__ == "__main__":
    app.run("0.0.0.0", "80", True, threaded=True)