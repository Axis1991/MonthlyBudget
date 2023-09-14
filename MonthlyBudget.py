from datetime import datetime
from flask import Flask, redirect, render_template, request, session, flash
from functs import (
    db_create,
    add_shopping_items,
    read_shopping_data,
    sum_up_expenses,
    add_user,
    get_user_id,
    HAPPY_FACE,
    SAD_FACE,
)
from models import Shopping, Users
import sqlite3

app = Flask(__name__)
app.secret_key = "E-)O.[1i]-U3W'c"

TITLE = "Monthly expenses 2023"
YEAR = 2023


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
        add_user(new_user)  # dodać id
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

@app.route("/month_selection", methods=["GET", "POST"])
def month_selection() -> str:
    if request.method == "POST":
        month = request.form["month"]
        session["month"] = month
        return redirect("/add_entry")
    return render_template(
        "monthselection.html",
        the_title=TITLE,
    )

@app.route("/add_entry", methods=["GET", "POST"])
def add_entry() -> str:
        month = session["month"]
        
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
            "add_entry.html",
            the_title=TITLE,
            the_month=month

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


# Następnym razem:

# testy - jak sprawdzić z plikami/bazami danych?
# co dalej z projektem?

# https://docs.python-guide.org/writing/structure/ - dostosować wymagania
# --  id w klasie user --> Jak i po co? jest w DB autoincrement
# dodać widok miesiąca - datetime - kratki tabela  - kiedy jest pierwszy z date time
