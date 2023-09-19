import calendar
from datetime import datetime
import sqlite3
from flask import redirect, flash, render_template
from models import Shopping, Users


HAPPY_FACE = r'<img src="https://cdn-icons-png.flaticon.com/512/214/214251.png" width=30px height=30px alt="Yes!">'
SAD_FACE = r'<img src="https://cdn-icons-png.flaticon.com/512/982/982991.png" width=30px height=30px alt="Nope =()">'
SHOPPING_DATA = "date, cost, item, satisfaction"
TITLE = "Monthly expenses"


def db_create() -> None:
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS purchases (userid, date, cost, item, satisfaction)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (userid INTEGER PRIMARY KEY AUTOINCREMENT, username NOT NULL, password NOT NULL)"
    )


def add_shopping_items(entry: Shopping) -> None:
    # [Shopping]
    userid = str(entry.userid)
    date = entry.date
    cost = entry.value
    item = entry.item
    satisfaction = entry.happy
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO purchases (userid, date, cost, item, satisfaction) values (?, ?, ?, ?, ?)",
        (userid, date, cost, item, satisfaction),
    )
    con.commit()
    cur.close()
    con.close()


def get_month_number(month: str) -> int:
    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    month_no = 0
    for key, value in months.items():
        if key == month:
            month_no = value
    return month_no

def parse_date(date: datetime) -> str:
    ready_date = date.strftime('%Y-%m-%d')
    return ready_date



def get_month_info(year, month) -> list:
    weekday, no_of_days = calendar.monthrange(year, month)
    skip_count = 0
    while skip_count < weekday:
        skip_count += 1
    month_list = []
    for _ in range(skip_count):
        month_list.append("*")
    day_num = 1
    for _ in range(no_of_days):
        month_list.append(str(day_num))
        day_num += 1
    boxes_to_fill = 7 - (len(month_list) % 7)
    for _ in range(boxes_to_fill):
        month_list.append("*")
    month_list_ready = [month_list[i:i+7] for i in range(0, len(month_list), 7)]
    return month_list_ready


def add_user(new_user: Users) -> None:
    username = new_user.username
    password = new_user.password
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username, password) values (?, ?)", (username, password)
    )
    con.commit()
    cur.close()
    con.close()


def get_user_id(current_username, current_password) -> int:
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    print(current_username, current_password)
    res = cur.execute(
        f"SELECT userid from users WHERE username ='{current_username}' AND password = '{current_password}'"
    )
    tuple_ = res.fetchone()
    id = tuple_[0]
    return id


def read_users_test() -> None:
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute("SELECT * from users")
    data = res.fetchall()
    print(data)


def read_shopping_data(current_userid):
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT {SHOPPING_DATA} from purchases WHERE userid = '{current_userid}'"
    )
    return res.fetchall()


def sum_up_expenses(data):
    total = 0
    for each in data:
        day, value, item, satisfaction = each
        total += float(value)
    return total


if __name__ == "__main__":
    read_users_test()
