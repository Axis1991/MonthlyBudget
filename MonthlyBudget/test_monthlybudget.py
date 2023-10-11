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
)

@pytest.mark.parametrize("month_items_satiscaction, expected_output", [
    (["!", "!", "!", "*", "*", "@", "@"], " good"),
    (["!", "*", "*", "@", "@", "@", "@"], " rather disappointing"),
    (["!", "*", "*", "@", "*", "*", "!"], "n average"),
    ([], "n average"),
    (["*", "*", "*", "*", "*"], "n average"),
])
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

    monkeypatch.setattr('MonthlyBudget.sqlite3.connect', Mock(return_value=mock_conn))

    try:
        check_unique_username("newuser")
    except ValueError:
        assert False, "Unexpected ValueError raised."

def test_check_unique_username_not_unique(monkeypatch):
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (1,)

    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('MonthlyBudget.sqlite3.connect', Mock(return_value=mock_conn))

    with pytest.raises(ValueError):
        check_unique_username("existinguser")