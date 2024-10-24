import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
excel_file_path = os.getenv("EXCEL_FILE_PATH", "default/path/to/excel/file.xlsx")
user_settings_path = os.getenv("USER_SETTINGS_PATH", "default/path/to/user_settings.json")
alpha_vantage_url = os.getenv("ALPHA_VANTAGE_URL")


def get_greeting(current_time: datetime) -> str:
    """
    Определяет приветствие в зависимости от текущего времени.

    :param current_time: Текущее время в формате datetime.
    :return: Приветствие в виде строки.
    """
    hour: int = current_time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_data_from_excel(file_path: str) -> pd.DataFrame:
    """
    Получает данные из Excel файла.

    :param file_path: Путь к Excel файлу.
    :return: DataFrame с данными из файла или пустой DataFrame в случае ошибки.
    """
    try:
        df: pd.DataFrame = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки


def get_stock_data(stock_symbol: str) -> Dict[str, Any]:
    """
    Получает данные о стоимости акций по символу.

    :param stock_symbol: Символ акции.
    :return: Словарь с данными о стоимости акции или пустой словарь в случае ошибки.
    """
    try:
        response = requests.get(
            f"{alpha_vantage_url}?function=TIME_SERIES_INTRADAY"
            f"&symbol={stock_symbol}&interval=5min"
            f"&apikey={api_key}&datatype=json"
        )
        data = response.json()

        if "Error Message" in data:
            print(
                f"Ошибка при получении данных для акции {stock_symbol}: {data['Error Message']}"
            )
            return {}
        return data
    except Exception as e:
        print(f"Ошибка при получении данных для акции {stock_symbol}: {e}")
        return {}


def get_market_data(
    currencies: List[str], stocks: List[str]
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Получает курсы валют и стоимость акций.

    :param currencies: Список валют для получения курсов.
    :param stocks: Список акций для получения стоимости.
    :return: Кортеж, содержащий список курсов валют и словарь с ценами акций.
    """
    currency_rates: List[Dict[str, Any]] = []
    stock_prices: Dict[str, float] = {}

    # Получение курсов валют
    for currency in currencies:
        try:
            response = requests.get(
                f"{alpha_vantage_url}?function=CURRENCY_EXCHANGE_RATE"
                f"&from_currency={currency}&to_currency=RUB"
                f"&apikey={api_key}"
            )
            data = response.json()
            if "Error Message" in data:
                print(
                    f"Ошибка при получении данных для валюты {currency}: {data['Error Message']}"
                )
            elif "Realtime Currency Exchange Rate" in data:
                rate = float(
                    data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
                )
                currency_rates.append({"currency": currency, "rate": rate})
            else:
                print(f"Неизвестный формат ответа для валюты {currency}: {data}")
        except Exception as e:
            print(f"Ошибка при получении данных для валюты {currency}: {e}")

    # Получение стоимости акций
    for stock in stocks:
        stock_data = get_stock_data(stock)
        if stock_data:
            if "Time Series (5min)" in stock_data:
                latest_time = next(iter(stock_data["Time Series (5min)"]))
                latest_close = stock_data["Time Series (5min)"][latest_time]["4. close"]
                stock_prices[stock] = float(latest_close)
            else:
                print(
                    f"Ошибка: 'Time Series (5min)' не найден для акции {stock}: {stock_data}"
                )
        else:
            print(f"Не удалось получить данные для акции {stock}")

    return currency_rates, stock_prices


def get_main(date_time_str: str) -> str:
    """
    Главная функция для анализа транзакций и получения рыночных данных.

    :param date_time_str: Дата и время в формате 'YYYY-MM-DD HH:MM:SS' для анализа транзакций.
    :return: JSON-строка с результатами анализа, включая приветствие, сводку по картам,
    топ-5 транзакций, курсы валют и цены акций.
    """
    # Преобразование строки в datetime для анализа транзакций
    analysis_time: datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

    # Получение текущего времени для приветствия
    current_time: datetime = datetime.now()

    # Получение приветствия
    greeting: str = get_greeting(current_time)

    # Чтение пользовательских настроек
    with open(user_settings_path, "r", encoding="utf-8") as f:
        user_settings: Dict[str, Any] = json.load(f)

    # Получение данных из Excel
    operations_data: pd.DataFrame = get_data_from_excel(excel_file_path)

    # Определяем первый день месяца
    start_date: datetime = analysis_time.replace(day=1)  # Первый день месяца
    end_date: datetime = analysis_time  # Конечная дата - введенная дата

    # Фильтрация данных по дате
    operations_data["Дата операции"] = pd.to_datetime(
        operations_data["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    filtered_data: pd.DataFrame = operations_data[
        (operations_data["Дата операции"] >= start_date)
        & (operations_data["Дата операции"] <= end_date)
    ]

    # Обработка данных по картам
    card_summary: Dict[str, Dict[str, float]] = {}
    for index, row in filtered_data.iterrows():
        card_number: str = (
            str(row["Номер карты"]).replace("*", "").strip()
        )  # Убираем символ '*' и пробелы
        amount: float = (
            float(row["Сумма операции"]) if pd.notna(row["Сумма операции"]) else 0.0
        )  # Приведение к float с проверкой на NaN
        status: str = str(row["Статус"])  # Приведение к строке

        # Пропускаем строки с пустыми номерами карт или суммами, а также с неуспешными транзакциями
        if len(card_number) < 4 or amount == 0.0 or status != "OK":
            continue  # Пропускаем итерацию, если номер карты менее 4 цифр, сумма 0 или статус не OK

        last_four_digits: str = card_number[-4:]  # Получаем последние 4 цифры
        total_spent: float = abs(amount)  # Сумма расходов
        cashback: float = total_spent // 100  # Кэшбэк

        if last_four_digits not in card_summary:
            card_summary[last_four_digits] = {"total_spent": 0, "cashback": 0}

        card_summary[last_four_digits]["total_spent"] += total_spent
        card_summary[last_four_digits]["cashback"] += cashback

    # Преобразование в список для JSON-ответа
    card_summary_list: List[Dict[str, Any]] = [
        {
            "last_digits": last_digits,
            "total_spent": data["total_spent"],
            "cashback": data["cashback"],
        }
        for last_digits, data in card_summary.items()
    ]

    # Получение топ-5 транзакций
    top_transactions: pd.DataFrame = filtered_data.nlargest(5, "Сумма операции")[
        ["Дата операции", "Сумма операции", "Категория", "Описание"]
    ]
    top_transactions_list: List[Dict[str, Any]] = []
    for _, row in top_transactions.iterrows():
        top_transactions_list.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": row["Сумма операции"],
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    # Получение рыночных данных
    currency_rates, stock_prices = get_market_data(
        user_settings["user_currencies"], user_settings["user_stocks"]
    )

    # Формирование JSON-ответа
    response: Dict[str, Any] = {
        "greeting": greeting,
        "cards": card_summary_list,  # Используем новый список
        "top_transactions": top_transactions_list,
        "currency_rates": currency_rates,
        "stock_prices": [
            {"stock": stock, "price": price} for stock, price in stock_prices.items()
        ],
    }

    return json.dumps(response, ensure_ascii=False, indent=2)
