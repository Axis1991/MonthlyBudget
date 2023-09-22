from datetime import datetime
from flask import Flask, redirect, render_template, request, session, flash
from functs import (
    db_create,
    add_shopping_items,
    read_shopping_data,
    sum_up_expenses,
    add_user,
    get_user,
    get_month_info,
    get_month_number,
    parse_date,
    repack_for_render,
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
        add_user(new_user)
        return redirect("/login")

    return render_template("register.html", the_title=TITLE)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        session["password"] = request.form["password"]
        try:
            current_user = get_user(session["username"], session["password"])
            session["id"] = current_user.id
            # print("main - session id", current_user.id)
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
    month_no = get_month_number(month)
    month_data = get_month_info(YEAR, month_no)
    # dodaj info czy jest zakup
    if request.method == "POST":
        print("main add entry session id", session["id"])
        userid = session["id"]
        item = request.form["item"]
        day = request.form["day"]
        value = request.form["value"]
        try:
            if request.form["happy"]:
                happy = HAPPY_FACE
        except KeyError:
            happy = SAD_FACE
        raw_date = datetime(YEAR, month_no, int(day))
        date = parse_date(raw_date)
        entry = Shopping(userid, date, value, item, happy)
        print(entry)
        add_shopping_items(entry)
        return redirect("/results")
    return render_template(
        "add_entry.html",
        the_title=TITLE,
        the_month=month,
        the_month_data=month_data
    )


@app.route("/results", methods=["GET", "POST"])
def results() -> str:
    current_userid = session["id"]
    print("main results session id", session["id"])
    shopping_list = read_shopping_data(current_userid)
    sum_of_expenses = sum_up_expenses(shopping_list)
    ready_list = repack_for_render(shopping_list)
    # print(ready_list)
    return render_template(
        "results.html",
        the_title=TITLE,
        shopping_list=ready_list,
        sum_of_expenses=sum_of_expenses,
    )


if __name__ == "__main__":
    app.run(debug=True)


# Następnym razem:

# https://www.sqlite.org/lang_returning.html - przeczytać id na koniec - Nie działa
#  dodaj id do shopping primary key auto - ok
# interaktywny miesiąc w dodatkowe info w liście 
# podaj miesiąc, rok ,dzien do shopping
# miesiąc w lukę w widoku
# https://flask.palletsprojects.com/en/2.3.x/quickstart/#variable-rules
# do miesiąca przyciski

# https://docs.python-guide.org/writing/structure/ - dostosować wymagania - ok?
