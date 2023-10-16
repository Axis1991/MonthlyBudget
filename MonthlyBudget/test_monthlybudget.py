import pytest
import calendar
from datetime import datetime
import sqlite3
from models import Shopping, Users
from unittest.mock import Mock


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
    read_date_from_url,
    read_month_shopping,
    repack_all_for_render,
    repack_for_render,
    sum_up_expenses,
    MONTHS_AND_NUMBERS,
)


@pytest.mark.parametrize(
    "month_items_satiscaction, expected_output",
    [
        (["!", "!", "!", "*", "*", "@", "@"], " good"),
        (["!", "*", "*", "@", "@", "@", "@"], " rather disappointing"),
        (["!", "*", "*", "@", "*", "*", "!"], "n average"),
        ([], "n average"),
        (["*", "*", "*", "*", "*"], "n average"),
    ],
)
def test_check_month_satisfaction(month_items_satiscaction, expected_output):
    result = check_month_satisfaction(month_items_satiscaction)
    assert result == expected_output


def test_check_month_length_valid_date():
    check_month_length(10, 10, 2023)


def test_check_month_length_invalid_date():
    with pytest.raises(ValueError):
        check_month_length(31, 4, 2023)


def test_check_month_length_leap_year():
    check_month_length(29, 2, 2024)


def test_check_month_length_non_leap_year():
    with pytest.raises(ValueError):
        check_month_length(29, 2, 2023)


def test_check_unique_username_unique(monkeypatch):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (0,)

    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr("MonthlyBudget.sqlite3.connect", Mock(return_value=mock_conn))

    try:
        check_unique_username("newuser")
    except ValueError:
        assert False, "Unexpected ValueError raised."


def test_check_unique_username_not_unique(monkeypatch):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (1,)

    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("MonthlyBudget.sqlite3.connect", Mock(return_value=mock_conn))

    with pytest.raises(ValueError):
        check_unique_username("existinguser")


def test_add_shopping_items_correct_entry(monkeypatch):
    mock_cursor = Mock()
    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("MonthlyBudget.sqlite3.connect", Mock(return_value=mock_conn))

    entry = Shopping(userid=1, date="2023-10-12", value=10.0, item="Cappy", happy=True)

    add_shopping_items(entry)

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO purchases (userid, date, value, item, happy) values (?, ?, ?, ?, ?)",
        (str(entry.userid), entry.date, entry.value, entry.item, entry.happy),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_add_shopping_items_incorrect_entry(monkeypatch):
    mock_cursor = Mock()
    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("MonthlyBudget.sqlite3.connect", Mock(return_value=mock_conn))

    entry = Shopping(
        wrongItem=1, data="2023-10-12", value=10.0, item="Cappy", happy=True
    )

    with pytest.raises(TypeError) as e_info:
        add_shopping_items(entry)

    assert not mock_cursor.execute.called
    assert not mock_conn.commit.called
    assert not mock_cursor.close.called


# jak można czy trzeba?


def test_add_user(monkeypatch):
    cursor = Mock()
    con = Mock()
    con.cursor.return_value = cursor
    monkeypatch.setattr("MonthlyBudget.sqlite3.connect", Mock(return_value=con))
    new_user = Users(username="testuser", password="testpassword")
    add_user(new_user)

    con.commit.assert_called_once()


def test_find_days_with_shopping_single_shopping_per_day():
    test_data = [
        Shopping(1, "2023-10-11", 124.3, "Lays", "yes", 1),
        Shopping(2, "2023-10-13", 424.3, "Cheetos", "no", 2),
    ]

    got = find_days_with_shopping(test_data)
    expected = {11: "!", 13: "@"}, ["!", "@"]

    assert got == expected


def test_find_days_with_shopping_diff_shopping_one_day():
    test_data = [
        Shopping(1, "2023-10-11", 124.3, "Lays", "yes", 1),
        Shopping(2, "2023-10-11", 424.3, "Cheetos", "no", 2),
    ]

    got = find_days_with_shopping(test_data)
    expected = {11: "&"}, ["&"]

    assert got == expected


def test_find_days_with_shopping_diff_shopping_one_day():
    test_data = [
        Shopping(1, "2023-10-11", 124.3, "Lays", "yes", 1),
        Shopping(2, "2023-10-11", 424.3, "Cheetos", "no", 2),
    ]

    got = find_days_with_shopping(test_data)
    expected = {11: "&"}, ["&"]

    assert got == expected


def test_find_days_with_shopping_no_shopping():
    test_data = []

    got = find_days_with_shopping(test_data)
    expected = {}, []

    assert got == expected


@pytest.mark.parametrize(
    "year, month, days_shopping, weeks_expected, month_list_expected",
    [
        (
            2023,
            10,
            {11: "!"},
            6,
            [
                ["*", "*", "*", "*", "*", "*", "1"],
                ["2", "3", "4", "5", "6", "7", "8"],
                ["9", "10", "11!", "12", "13", "14", "15"],
                ["16", "17", "18", "19", "20", "21", "22"],
                ["23", "24", "25", "26", "27", "28", "29"],
                ["30", "31", "*", "*", "*", "*", "*"],
            ],
        ),
        (
            2023,
            11,
            {12: "!", 13: "@", 14: "&"},
            5,
            [
                ["*", "*", "1", "2", "3", "4", "5"],
                ["6", "7", "8", "9", "10", "11", "12!"],
                ["13@", "14&", "15", "16", "17", "18", "19"],
                ["20", "21", "22", "23", "24", "25", "26"],
                ["27", "28", "29", "30", "*", "*", "*"],
            ],
        ),
        (
            2023,
            11,
            {},
            5,
            [
                ["*", "*", "1", "2", "3", "4", "5"],
                ["6", "7", "8", "9", "10", "11", "12"],
                ["13", "14", "15", "16", "17", "18", "19"],
                ["20", "21", "22", "23", "24", "25", "26"],
                ["27", "28", "29", "30", "*", "*", "*"],
            ],
        ),
    ],
)
def test_get_month_info(
    year, month, days_shopping, month_list_expected, weeks_expected
):
    month_list_ready, week_num = get_month_info(year, month, days_shopping)
    assert month_list_ready == month_list_expected
    assert week_num == weeks_expected


@pytest.mark.parametrize(
    "monthnumber, expected_output", [
        (12, "December"), 
        (1, "January"), 
        (7, "July")
        ]
)
def test_get_month_name(monthnumber, expected_output):
    assert get_month_name(monthnumber) == expected_output


@pytest.mark.parametrize(
    "monthname, expected_output", [
        ("December", 12), 
        ("January", 1), 
        ("July", 7)
        ]
)
def test_get_month_number(monthname, expected_output):
    assert get_month_number(monthname) == expected_output