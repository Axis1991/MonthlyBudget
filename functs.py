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
    date = entry.day_num
    cost = entry.value
    item = entry.item
    satisfaction = entry.happy
    print(userid, date, cost, item, satisfaction)
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO purchases (userid, date, cost, item,satisfaction) values (?, ?, ?, ?, ?)",
        (userid, date, cost, item, satisfaction),
    )
    con.commit()
    cur.close()
    con.close()


def add_user(new_user: Users):
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
    pass
