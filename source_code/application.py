from cs50 import SQL
from flask import Flask, redirect, request, render_template, session
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///people.db")

logged_in = False
current_user = ""


@app.route("/")
def index():
    if "logged_in" not in session:
        session["logged_in"] = False
    if "current_user" not in session:
        session["current_user"] = ""
    return render_template("index.html", logged_in=session["logged_in"])


@app.route("/sign_up", methods=["GET", "POST"])
def sing_up():
    if request.method == "GET":
        return render_template("sign_up.html")
    else:
        name = request.form.get("name")
        if not name:
            return render_template("apology.html", message="Debes incertar una nombre.")
        password = request.form.get("password")
        if not password:
            return render_template("apology.html", message="Debes incertar una contraseña.")

        #Checking the user, who wants to sign up, doesn't exist in the database
        users = db.execute("SELECT * FROM users")
        if len(users) > 0:
            for user in users:
                if user["name"] == name:
                    return render_template("apology.html", message="Este nombre de usuario ya ha sido tomado.")

        db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", name=name, password=password)
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        name = request.form.get("name")
        if not name:
            return render_template("apology.html", message="Debes introducir un nombre.")
        password = request.form.get("password")
        if not password:
            return render_template("apology.html", message="Debes introducir una contraseña.")

        users = db.execute("SELECT * FROM users")
        if len(users) == 0:
            return render_template("apology.html", message="Este nombre de usuario no existe.")

        for user in users:
            if user["name"] == name and user["password"] == password:
                session["logged_in"] = True
                session["current_user"] = user["name"]
                return redirect("/")
            elif user["name"] == name and user["password"] != password:
                return render_template("apology.html", message="Contraseña incorrecta.")

        return render_template("apology.html", message="Usuario inválido.")


@app.route("/session_end")
def session_end():
    session["logged_in"] = False
    return redirect("/")


@app.route("/lessons")
def lessons():
    return render_template("lessons.html")


@app.route("/lessons/present_simple")
def present_simple():
    return render_template("lessons/present_simple.html")


@app.route("/lessons/past_simple")
def past_simple():
    return render_template("lessons/past_simple.html")


@app.route("/lessons/future_simple")
def future_simple():
    return render_template("lessons/future_simple.html")


@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return render_template("lessons/test.html")
    else:
        score = 0
        user_answers = []
        for i in range(1, 11):
            answer = request.form.get("q"+str(i))
            user_answers.append(answer.lower().strip())

        correct_answers = [["don't like", "do not like"], ["likes"], ["were"], ["be"], ["will go"], ["broke"], ["wants"], ["doesn't love", "does not love"], ["has"], ["bought"]]

        for i in range(0, 10):
            if user_answers[i] in correct_answers[i]:
                score += 1

        list_of_dicts_max_score = db.execute("SELECT max_score FROM users WHERE name = ?", session["current_user"])
        max_score = list_of_dicts_max_score[0]["max_score"]

        if max_score == None or max_score < score:
            max_score = score

        db.execute("UPDATE users SET max_score = ? WHERE name = ?", max_score, session["current_user"])

        return render_template("lessons/score.html", score=score)


@app.route("/ranking")
def ranking():
    ranking = db.execute("SELECT name, max_score FROM users ORDER BY max_score DESC")
    return render_template("lessons/ranking.html", ranking=ranking, len_ranking=len(ranking))