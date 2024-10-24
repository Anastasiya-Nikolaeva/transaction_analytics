import json
import os
import sys
from datetime import datetime

import pandas as pd

from src.reports import (expenses_by_category, expenses_by_weekday,
                         expenses_by_workday, load_data)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


def test_load_data_success(mocker):
    # Создаем фиктивный DataFrame для успешного теста
    mock_df = pd.DataFrame({"column1": [1, 2], "column2": [3, 4]})
    mock_read_excel = mocker.patch(
        "reports.pd.read_excel", return_value=mock_df
    )  # Патчим pd.read_excel в модуле reports

    result = load_data("fake_path.xlsx")

    # Проверяем, что результат соответствует ожидаемому DataFrame
    pd.testing.assert_frame_equal(result, mock_df)
    mock_read_excel.assert_called_once_with("fake_path.xlsx")


def test_load_data_failure(mocker):
    # Настраиваем mock для генерации исключения
    mock_read_excel = mocker.patch(
        "reports.pd.read_excel", side_effect=Exception("File not found")
    )  # Патчим pd.read_excel в модуле reports

    result = load_data("fake_path.xlsx")

    # Проверяем, что результат равен None при ошибке
    assert result is None
    mock_read_excel.assert_called_once_with("fake_path.xlsx")


def test_expenses_by_category(data_test):
    date = pd.Timestamp("2021-12-31")

    result = expenses_by_category(data_test, "Супермаркеты", date)
    expected_result = {
        "category": "Супермаркеты",
        "total_expense": -1221.06,
        "date": "2021-12-31",
    }
    assert json.loads(result) == expected_result


def test_expenses_by_weekday(data_test):
    weekdays = ["Friday", "Thursday", "Wednesday"]
    result = expenses_by_weekday(data_test, weekdays)
    expected_result = {
        "total_expenses": {
            "Friday": -1785.06,
            "Thursday": -200203.39,
            "Wednesday": -2822.80,
        },
        "weekdays": weekdays,
    }
    assert json.loads(result) == expected_result


def test_expenses_by_workday(data_test):
    date = datetime(2021, 12, 31)
    result = expenses_by_workday(data_test, "Супермаркеты", date)
    expected_result = {
        "category": "Супермаркеты",
        "workday_expense": -1221.06,
        "weekend_expense": 0.0,
        "date": "2021-12-31",
    }
    assert json.loads(result) == expected_result
