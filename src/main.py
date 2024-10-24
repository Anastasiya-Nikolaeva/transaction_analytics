import logging
import os
from datetime import datetime
from pprint import pprint

import pandas as pd

from src.reports import (expenses_by_category, expenses_by_weekday,
                         expenses_by_workday, load_data)
from src.services import get_personal_transfers
from src.views import get_main

excel_file_path = os.getenv("EXCEL_FILE_PATH")

if __name__ == "__main__":
    file_path = excel_file_path
    df = load_data(file_path)

    transfers_json = get_personal_transfers(file_path)
    logging.info("Найденные переводы физическим лицам")
    pprint(transfers_json)

    if df is not None:
        # Преобразуем столбец 'Дата операции' в datetime
        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
        )

        # Пример вызова функций
        category_expenses = expenses_by_category(df, "Супермаркеты", datetime.now())
        weekday_expenses = expenses_by_weekday(df)
        workday_weekend_expenses = expenses_by_workday(
            df, "Супермаркеты", datetime.now()
        )

        print("Траты по категории:", category_expenses)
        print("Траты по дням недели:", weekday_expenses)
        print("Траты в рабочий/выходной день:", workday_weekend_expenses)

        date_time_input: str = "2021-12-25 19:59:44"
        result: str = get_main(date_time_input)
        print(result)
