from flask import Flask, redirect, render_template, request, session, flash
from functs import (
    db_create,
    add_shopping_items,
    read_shopping_data,
    sum_up_expenses,
    add_user,
    get_user_id,
    HAPPY_FACE,
    SAD_FACE
)
from models import Shopping, Users
import sqlite3

app = Flask(__name__)
app.secret_key = "E-)O.[1i]-U3W'c"

TITLE = "Monthly expenses"

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    db_create()
    if "username" in session:
        username = session["username"]
        return render_template("info.html", username=username)
    else:
        return render_template("login.html", the_title=TITLE)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        new_user = Users(username, password)
        add_user(new_user)
        return redirect("/index")

    return render_template("register.html", the_title=TITLE)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        session["password"] = request.form["password"]
        print(session["username"], session["password"])
        try:
            session["id"] = get_user_id(session["username"], session["password"])
            print(session["id"])
            return redirect("/index")
        except sqlite3.OperationalError:
            flash("Username or password are incorrect, or there is no such account.")
            return render_template(
                "login.html",
                the_title=TITLE,
            )
        except TypeError:
            flash("Username or password are incorrect, or there is no such account.")
            return render_template(
                "login.html",
                the_title=TITLE,
            )
    else:
        return render_template(
            "login.html",
            the_title=TITLE,
        )


@app.route("/log_out", methods=["GET", "POST"])
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    session.pop("password", None)
    session.pop("id", None)
    return redirect("/index")


@app.route("/add_entry", methods=["GET", "POST"])
def add_entry() -> str:
    if request.method == "POST":
        userid = session["id"]
        item = request.form["item"]
        day_num = request.form["day"]
        value = request.form["value"]
        try:
            if request.form["happy"]:
                happy = HAPPY_FACE
        except KeyError:
            happy = SAD_FACE
        entry = Shopping(userid, day_num, item, value, happy)
        add_shopping_items(entry)
        return redirect("/results")
    return render_template(
        "add_entry.html", the_title=TITLE, 
    )


@app.route("/results", methods=["GET", "POST"])
def results() -> str:
    current_userid = session["id"]
    shopping_list = read_shopping_data(current_userid)
    sum_of_expenses = sum_up_expenses(shopping_list)

    return render_template(
        "results.html",
        the_title=TITLE,
        shopping_list=shopping_list,
        sum_of_expenses=sum_of_expenses,
    )


if __name__ == "__main__":
    app.run(debug=True)



# https://flask.palletsprojects.com/en/2.3.x/quickstart/#sessions


# klasa użytkownik (name password) - ok
# id w bazie danych w tabeli (id username password - auto increment do id - https://www.sqlitetutorial.net/sqlite-autoincrement/ - primary key. - done ok

# - widok login - odczytaj login hasło z formularza, select z tabelki users, nie udało się zalogować. - ok???

# w template strony miesjce na komunikat - spróbować flash - działa

# obrazki we flask - zobaczyć w quickstar static files
# https://flask.palletsprojects.com/en/2.3.x/quickstart/#static-files

# models.py -> nowy plik na klasy - ok

# https://flask.palletsprojects.com/en/2.3.x/patterns/flashing/ - ok


# Następnym razem:

# git ssh - klucze
# api - o co w ogóle chodzi?
# testy - jak sprawdzić z plikami/bazami danych?
# licencja git
# co dalej z projektem?
