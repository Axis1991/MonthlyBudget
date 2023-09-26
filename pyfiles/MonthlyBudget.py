from datetime import datetime
from flask import Flask, redirect, render_template, request, session, flash
from models import Shopping, Users
import sqlite3

from functs import (
    add_shopping_items,
    add_user,
    check_month_length,
    check_month_satisfaction,
    check_unique_username,
    db_create,
    delete_shopping_entry,
    find_days_with_shopping,
    get_month_info,
    get_month_name,
    get_month_number,
    get_user,
    parse_date,
    read_all_shopping,
    read_daily_shopping,
    read_month_shopping,
    repack_all_for_render,
    repack_for_render,
    sum_up_expenses,
)

app = Flask(__name__, template_folder='../templates', static_folder='../static')
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


@app.route("/add_entry", methods=["GET", "POST"])
def add_entry() -> str:
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
        try:
            check_month_length(int(day), month_no, int(year))
        except ValueError:
            flash("This month doesn't have so many days!")
            return render_template("add_entry.html", the_title=TITLE)
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


@app.route("/change_session", methods=["GET", "POST"])
def change_session():
    month = request.form["month"]
    if month[0] == "0":
        month = month[1:]
    year = request.form["year"]
    session["year"] = year
    session["month"] = get_month_name(int(month))
    return redirect("/month_view")


@app.route("/daily", methods=["GET", "POST"])
def daily() -> str:
    if request.method == "POST":
        month_str = session["month"]
        year = int(session["year"])
        month = get_month_number(month_str)
        userid = session["id"]
        day = int(request.form["day"])
        shopping_list = read_daily_shopping(month, year, day, userid)
        sum_of_expenses = sum_up_expenses(shopping_list)
        ready_list = repack_for_render(shopping_list)
        return render_template(
            "daily.html",
            the_title=f"{month_str} {day}",
            shopping_list=ready_list,
            sum_of_expenses=sum_of_expenses,
        )
    else:
        return redirect("/month_view")
    
@app.route("/delete_entry", methods=["GET", "POST"])
def delete_entry():
    id_to_delete = int(request.form["id_to_delete"])
    delete_shopping_entry(id_to_delete)
    return redirect("/month_view")


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
    session.pop("username", None)
    session.pop("password", None)
    session.pop("id", None)
    session.pop("month", None)
    session.pop("year", None)
    return redirect("/index")


@app.route("/month_view", methods=["GET", "POST"])
def month_view() -> str:
    try:
        month_str = session["month"]
        year = int(session["year"])
    except KeyError:
        today = datetime.now()
        month = today.month
        session["month"] = get_month_name(month)
        month_str = session["month"]
        year = today.year
        session["year"] = year
    month = get_month_number(month_str)
    userid = session["id"]
    shopping_data = read_month_shopping(month, year, userid)
    days_for_render, satisfaction = find_days_with_shopping(shopping_data)
    month_satisfaction = check_month_satisfaction(satisfaction)
    month_data, week_num = get_month_info(year, month, days_for_render)
    sum_of_expenses = sum_up_expenses(shopping_data)
    shopping_for_render = repack_for_render(shopping_data)

    return render_template(
        "monthview.html",
        the_title=TITLE,
        the_month_data=month_data,
        the_shopping_data=shopping_for_render,
        the_month=month_str,
        the_year=year,
        sum_of_expenses=sum_of_expenses,
        the_weeks=week_num,
        the_month_satisfaction=month_satisfaction,
    )


@app.route("/previous_month", methods=["GET", "POST"])
def previous_month() -> str:
    month_str = session["month"]
    month_no = get_month_number(month_str) - 1
    new_month = get_month_name(month_no)
    session["month"] = new_month
    if month_no == 0:
        session["month"] = "December"
        year = int(session["year"]) - 1
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
        year = int(session["year"]) + 1
        session["year"] = year
    return redirect("/month_view")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            check_unique_username(username)
            new_user = Users(username, password)
            add_user(new_user)
            return redirect("/login")
        except ValueError:
            flash("Username already registered. Please choose a different one.")
            render_template("register.html", the_title=TITLE)
    return render_template("register.html", the_title=TITLE)


@app.route("/results", methods=["GET", "POST"])
def results() -> str:
    current_userid = session["id"]
    shopping_list = read_all_shopping(current_userid)
    sum_of_expenses = sum_up_expenses(shopping_list)
    ready_list = repack_all_for_render(shopping_list)
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
