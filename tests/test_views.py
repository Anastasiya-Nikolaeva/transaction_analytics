import json
from datetime import datetime

from src.views import get_greeting, get_main, get_market_data, get_stock_data


def test_get_greeting():
    # Тестируем функцию get_greeting
    current_time = datetime.strptime("2023-10-01 09:00:00", "%Y-%m-%d %H:%M:%S")
    greeting = get_greeting(current_time)
    assert greeting == "Доброе утро"


def test_get_data_from_excel(data_test):
    # Тестируем функцию get_data_from_excel
    df = data_test
    assert len(df) == 16
    assert df["Сумма операции"][0] == -160.89


def test_get_stock_data(mocker):
    # Тестируем функцию get_stock_data
    mock_response = {
        "Time Series (5min)": {
            "2023-10-01 10:00:00": {
                "1. open": "100.00",
                "2. high": "101.00",
                "3. low": "99.00",
                "4. close": "100.50",
                "5. volume": "1000",
            }
        }
    }
    mocker.patch("requests.get", return_value=mocker.Mock(json=lambda: mock_response))

    stock_data = get_stock_data("AAPL")
    assert "Time Series (5min)" in stock_data
    assert (
        float(stock_data["Time Series (5min)"]["2023-10-01 10:00:00"]["4. close"])
        == 100.50
    )


def test_get_market_data(mocker, data_test):
    # Тестируем функцию get_market_data
    mock_currency_response = {
        "Realtime Currency Exchange Rate": {"5. Exchange Rate": "75.00"}
    }
    mock_stock_response = {
        "Time Series (5min)": {
            "2023-10-01 10:00:00": {
                "1. open": "100.00",
                "2. high": "101.00",
                "3. low": "99.00",
                "4. close": "100.50",
                "5. volume": "1000",
            }
        }
    }

    mocker.patch(
        "requests.get",
        side_effect=[
            mocker.Mock(json=lambda: mock_currency_response),  # Для валюты
            mocker.Mock(json=lambda: mock_stock_response),  # Для акций
        ],
    )

    currencies = ["USD"]
    stocks = ["AAPL"]
    currency_rates, stock_prices = get_market_data(currencies, stocks)

    assert len(currency_rates) == 1
    assert currency_rates[0]["rate"] == 75.00
    assert "AAPL" in stock_prices
    assert stock_prices["AAPL"] == 100.50


def test_get_main(mocker, data_test):
    # Тестируем функцию main
    mocker.patch("src.views.get_data_from_excel", return_value=data_test)
    mocker.patch(
        "src.views.get_market_data",
        return_value=([{"currency": "USD", "rate": 75.00}], {"AAPL": 100.50}),
    )

    result = get_main("2021-12-30 12:00:00")  # Изменено на 30 декабря 12:00:00
    response = json.loads(result)

    # Проверяем наличие приветствия
    assert "greeting" in response
    # Проверяем, что есть данные по картам
    assert len(response["cards"]) > 0
    # Проверяем, что -300.00 есть в топ-транзакциях (это сумма, соответствующая 30 декабря)
    assert any(tx["amount"] == -300.00 for tx in response["top_transactions"])
    # Проверяем, что есть курсы валют
    assert len(response["currency_rates"]) == 1
    assert response["currency_rates"][0]["currency"] == "USD"
    # Проверяем, что есть данные по акциям
    assert len(response["stock_prices"]) == 1
    assert response["stock_prices"][0]["stock"] == "AAPL"
    assert response["stock_prices"][0]["price"] == 100.50
