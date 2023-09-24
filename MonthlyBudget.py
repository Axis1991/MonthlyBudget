from datetime import datetime
from flask import Flask, redirect, render_template, request, session, flash
from functs import (
    db_create,
    add_shopping_items,
    read_all_shopping,
    sum_up_expenses,
    add_user,
    get_user,
    get_month_info,
    get_month_number,
    parse_date,
    repack_for_render,
    get_month_name,
    read_month_shopping,
    find_days_with_shopping,
    HAPPY_FACE,
    SAD_FACE,
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


@app.route("/month_view", methods=["GET", "POST"])
def month_view() -> str:
    # print(session["month"],session["year"])
    month_str = session["month"]
    year = int(session["year"])
    month = get_month_number(month_str)
    userid = session["id"]
    shopping_data = read_month_shopping(month, year, userid)
    days_shopping = (find_days_with_shopping(shopping_data))
    print(days_shopping)
    month_data = get_month_info(year,month,days_shopping)
    sum_of_expenses = sum_up_expenses(shopping_data)
    shopping_for_render = repack_for_render(shopping_data)

    return render_template(
        "monthview.html",
        the_title=TITLE,
        the_month_data = month_data,
        the_shopping_data = shopping_for_render,
        the_month = month_str,
        the_year = year,
        sum_of_expenses=sum_of_expenses
    )


@app.route("/previous_month", methods=["GET", "POST"])
def previous_month() -> str:
    month_str = session["month"]
    month_no = get_month_number(month_str) - 1
    new_month = get_month_name(month_no)
    session["month"] = new_month
    if month_no == 0:
        session["month"] = "December"
        year = int(session["year"])-1
        session["year"] = year
    return redirect("/month_view")


@app.route("/next_month", methods=["GET", "POST"])
def next_month() -> str:
    month_str = session["month"]
    month_no = get_month_number(month_str) + 1
    new_month = get_month_name(month_no)
    session["month"] = new_month
    year = session["year"]
    if month_no == 13:
        session["month"] = "January"
        year = int(session["year"])+1
        session["year"] = year
    return redirect("/month_view")


@app.route("/add_entry", methods=["GET", "POST"])
def add_entry() -> str:
    # month = session["month"]
    # month_no = get_month_number(month)
    if request.method == "POST":
        userid = session["id"]
        item = request.form["item"]
        day = request.form["day"]
        month = request.form["month"]
        year = request.form["year"]
        value = request.form["value"]
        try:
            if request.form["happy"]:
                happy = "yes"
        except KeyError:
            happy = "no"
        month_no = get_month_number(month)
        raw_date = datetime(int(year), month_no, int(day))
        date = parse_date(raw_date)
        entry = Shopping(userid, date, value, item, happy)
        add_shopping_items(entry)
        session["month"] = month
        session["year"] = year
        return redirect("/month_view")
    return render_template(
        "add_entry.html",
        the_title=TITLE,
    )


@app.route("/results", methods=["GET", "POST"])
def results() -> str:
    current_userid = session["id"]
    shopping_list = read_all_shopping(current_userid)

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
# podaj miesiąc, rok ,dzien do shopping - ok
# miesiąc w lukę w widoku - no idea
# https://flask.palletsprojects.com/en/2.3.x/quickstart/#variable-rules
# do miesiąca przyciski

# https://docs.python-guide.org/writing/structure/ - dostosować wymagania
