import json

import pandas as pd

from src.services import get_personal_transfers


def test_valid_transfers(data_test, monkeypatch):
    # Подменяем pd.read_excel, чтобы использовать данные из фикстуры
    monkeypatch.setattr(pd, "read_excel", lambda _: data_test)

    # Вызов функции
    result = get_personal_transfers("dummy_path.xlsx")

    # Ожидаемый результат (только переводы)
    expected_result = [
        {"Перевод": -800.00, "Фамилия": "Константин Л."},
        {"Перевод": -20000.00, "Фамилия": "Константин Л."},
    ]

    # Проверка, что результат соответствует ожидаемому
    assert json.loads(result) == expected_result


def test_no_transfers(data_new_test, monkeypatch):
    monkeypatch.setattr(pd, "read_excel", lambda _: data_new_test)

    result = get_personal_transfers("dummy_path.xlsx")

    expected_result = []

    assert json.loads(result) == expected_result


def test_invalid_file(monkeypatch):
    # Имитация ошибки при чтении файла
    monkeypatch.setattr(
        pd,
        "read_excel",
        lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Ошибка чтения")),
    )

    # Вызов функции
    result = get_personal_transfers("dummy_path.xlsx")
    expected_result = {"error": "Ошибка при чтении файла Excel."}
    assert json.loads(result) == expected_result
