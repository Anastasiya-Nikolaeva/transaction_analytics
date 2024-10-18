import json
import logging
from datetime import timedelta

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def load_data(file_path):
    """Загрузка данных из Excel"""
    try:
        df = pd.read_excel(file_path)
        logging.info("Данные успешно загружены из Excel.")
        return df
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
        return None


def expenses_by_category(df, category, date):
    """Функция для отчета 'Траты по категории'"""
    three_months_ago = date - timedelta(days=90)
    filtered_df = df[
        (df["Категория"] == category)
        & (df["Дата операции"] >= three_months_ago)
        & (df["Дата операции"].dt.date <= date.date())
    ]

    total_expense = filtered_df["Сумма операции"].sum()

    result = {
        "category": category,
        "total_expense": total_expense,
        "date": date.strftime("%Y-%m-%d"),
    }

    return json.dumps(result)


def expenses_by_weekday(df, weekdays=None):
    """Функция для отчета 'Траты по дням недели'"""
    if weekdays is None:
        weekdays = df["Дата операции"].dt.day_name().unique().tolist()

    df["День недели"] = df["Дата операции"].dt.day_name()

    # Фильтруем DataFrame по указанным дням недели
    df_filtered = df[df["День недели"].isin(weekdays)]

    total_expenses = df_filtered.groupby("День недели")["Сумма операции"].sum()

    result = {"total_expenses": total_expenses.to_dict(), "weekdays": weekdays}

    return json.dumps(result)


def expenses_by_workday(df, category, date):
    """Функция для отчета 'Траты в рабочий/выходной день'"""
    date_only = date.date()
    three_months_ago = date_only - timedelta(days=90)

    # Убедитесь, что 'Дата операции' имеет тип datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    # Фильтруем данные по категории и диапазону дат
    filtered_df = df[
        (df["Категория"] == category)
        & (df["Дата операции"].dt.date >= three_months_ago)
        & (df["Дата операции"].dt.date <= date_only)
    ].copy()  # Создаем явную копию, чтобы избежать предупреждений

    # Определяем рабочие и выходные дни
    filtered_df.loc[:, "День недели"] = filtered_df[
        "Дата операции"
    ].dt.dayofweek  # Используем .loc для изменения
    workday_expense = filtered_df[filtered_df["День недели"] < 5][
        "Сумма операции"
    ].sum()  # Пн-Пт
    weekend_expense = filtered_df[filtered_df["День недели"] >= 5][
        "Сумма операции"
    ].sum()  # Сб-Вс

    result = {
        "category": category,
        "workday_expense": workday_expense,
        "weekend_expense": weekend_expense,
        "date": date_only.strftime("%Y-%m-%d"),
    }

    return json.dumps(result)


# if __name__ == "__main__":
#     file_path = "../data/operations.xlsx"
#     df = load_data(file_path)
#
#     if df is not None:
#         # Преобразуем столбец 'Дата операции' в datetime
#         df["Дата операции"] = pd.to_datetime(
#             df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
#         )
#
#         # Пример вызова функций
#         category_expenses = expenses_by_category(df, "Супермаркеты", datetime.now())
#         weekday_expenses = expenses_by_weekday(df)
#         workday_weekend_expenses = expenses_by_workday(
#             df, "Супермаркеты", datetime.now()
#         )
#
#         print("Траты по категории:", category_expenses)
#         print("Траты по дням недели:", weekday_expenses)
#         print("Траты в рабочий/выходной день:", workday_weekend_expenses)
