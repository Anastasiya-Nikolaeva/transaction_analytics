import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
excel_file_path = os.getenv("EXCEL_FILE_PATH", "default/path/to/excel/file.xlsx")
user_settings_path = os.getenv(
    "USER_SETTINGS_PATH", "default/path/to/user_settings.json"
)
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
