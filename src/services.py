import json
import logging
import re

import pandas as pd

logging.basicConfig(level=logging.INFO)


def get_personal_transfers(file_path):
    """
    Функция для поиска переводов физическим лицам.

    :param file_path: Путь к файлу Excel
    :return: JSON со всеми транзакциями, относящимися к переводам физ лицам
    """

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        logging.error("Ошибка при чтении файла Excel: %s", e)
        return json.dumps({"error": "Ошибка при чтении файла Excel."})

    result = []
    # Регулярное выражение для имени и первой буквы фамилии
    pattern = re.compile(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$")

    for index, row in df.iterrows():
        category = row["Категория"]
        description = row["Описание"]

        # Проверяем наличие столбца "Описание"
        if "Описание" in df.columns:
            description = row["Описание"]
        else:
            description = None

        if category == "Переводы":
            # Проверяем, соответствует ли описание шаблону
            if isinstance(description, str) and pattern.search(description):

                transfer_info = {
                    "Перевод": row["Сумма операции"],
                    "Фамилия": description,
                }
                result.append(transfer_info)

    return json.dumps(result, ensure_ascii=False)
