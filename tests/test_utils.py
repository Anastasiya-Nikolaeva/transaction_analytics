from datetime import datetime

from src.utils import get_stock_data
from src.views import get_greeting


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
