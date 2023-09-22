import calendar
from datetime import datetime
import sqlite3
# from flask import redirect, flash, render_template
from models import Shopping, Users


HAPPY_FACE = r'<img src="https://cdn-icons-png.flaticon.com/512/214/214251.png" width=30px height=30px alt="Yes!">'
SAD_FACE = r'<img src="https://cdn-icons-png.flaticon.com/512/982/982991.png" width=30px height=30px alt="Nope =()">'
SHOPPING_DATA = "userid, date, value, item, happy, itemID"
TITLE = "Monthly expenses"
MONTHS_AND_NUMBERS = {
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


def db_create() -> None:
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS purchases (userid, date, value, item, happy, itemID INTEGER PRIMARY KEY AUTOINCREMENT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (username NOT NULL, password NOT NULL, userid INTEGER PRIMARY KEY AUTOINCREMENT)"
    )
    con.commit()
    cur.close()
    con.close()


def add_shopping_items(entry: Shopping) -> None:
    userid = str(entry.userid)
    date = entry.date
    value = entry.value
    item = entry.item
    happy = entry.happy
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO purchases (userid, date, value, item, happy) values (?, ?, ?, ?, ?)",
        (userid, date, value, item, happy)
    )
    # dodać id zakupu z autoincrement - ok
    con.commit()
    cur.close()
    con.close()


def get_month_number(month: str) -> int:
    month_no = 0
    for key, value in MONTHS_AND_NUMBERS.items():
        if key == month:
            month_no = value
    return month_no

def get_month_name(month_no: str) -> int:
    for key, value in MONTHS_AND_NUMBERS.items():
        if value == month_no:
            return key

def parse_date(date: datetime) -> str:
    ready_date = date.strftime("%Y-%m-%d")
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
    month_list_ready = [month_list[i : i + 7] for i in range(0, len(month_list), 7)]
    return month_list_ready

def check_year_change(month_no):
    if month_no == 13:
        new_month = "January"
        year_diff = 1
        return new_month, year_diff
    elif month_no == 0:
        new_month = "December"
        year_diff = -1
        return new_month, year_diff
    else:
        pass


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


def get_user(current_username, current_password) -> int:
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT * from users WHERE username ='{current_username}' AND password = '{current_password}'"
    )
    user_data = res.fetchone()
    print("functs - get user", user_data)
    current_user = Users(username=user_data[0], password=user_data[1], id=user_data[2])
    print("functs", current_user)
    return current_user


def read_users_test() -> None:
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute("SELECT * from users")
    data = res.fetchall()
    print(data)

def read_shopping_test():
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute("SELECT * from purchases")
    data = res.fetchall()
    print(data)
    


def read_all_shopping(current_userid):
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT {SHOPPING_DATA} from purchases WHERE userid = '{current_userid}' ORDER BY date ASC"
    )
    shopping_data = res.fetchall()
    Shopping_class_data = pack_to_Shopping(shopping_data)
    return Shopping_class_data

def read_month_shopping(month: int, year:int, userid:int) -> list:
    month = "0"+str(month) if month < 10 else month
    date = f"{str(year)}-{month}"
    con = sqlite3.connect("shopping.db")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT {SHOPPING_DATA} from purchases WHERE userid = '{userid}' AND date LIKE '{date}%'  ORDER BY date ASC"
    )
    month_shopping = res.fetchall()
    Shopping_class_data = pack_to_Shopping(month_shopping)
    return Shopping_class_data

def pack_to_Shopping(shopping_data):
    list_of_items = []
    for e in shopping_data:
        item = Shopping(
            userid=e[0], date=e[1], value=e[2],item=e[3],  happy=e[4], itemID=e[5]
        )
        list_of_items.append(item)
    return list_of_items
    

def repack_for_render(obj_list: Shopping) -> list:
    list_for_render = []
    for item in obj_list:
        # print(item)
        single_item = []
        single_item.append(item.date)
        single_item.append(item.value)
        single_item.append(item.item)
        single_item.append(item.happy)
        list_for_render.append(single_item)
    return list_for_render



def sum_up_expenses(data: Shopping) -> float:
    total = 0
    for item in data:
        total += float(item.value)
    return total


if __name__ == "__main__":
    print(read_month_shopping(6,2023,1))
