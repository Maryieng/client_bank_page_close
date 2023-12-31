from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def write_result_to_file(filename=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename == f"{timestamp}.txt"
            with open(filename, "w", encoding='utf-8') as file:
                file.write(result.to_string(index=False))
            return result
        return wrapper
    return decorator


@write_result_to_file('my_result.txt')
def spending_by_category(operations: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """ Функция принимает на вход: датафрейм с транзакциями, название категории, опциональную дату,
     по умолчанию текущая дата. Функция возвращает операции по заданной категории за последние 3 месяца
     (от переданной даты)."""
    try:
        if date is None:
            date = datetime.now().date()  # type: ignore
        else:
            date = datetime.strptime(date, "%Y-%m-%d").date()  # type: ignore
        three_months_ago = date - timedelta(days=3 * 30)  # type: ignore
        filtered_df = operations.copy()
        filtered_df['Дата платежа'] = pd.to_datetime(filtered_df['Дата платежа'], dayfirst=True)
        filtered_df = filtered_df[(filtered_df['Категория'] == category)
                                  & (filtered_df['Дата платежа'] >= pd.to_datetime(three_months_ago))
                                  & (filtered_df['Дата платежа'] <= pd.to_datetime(date))]
        return filtered_df
    except Exception as e:
        print("Произошла ошибка:", str(e))
        return pd.DataFrame()


@write_result_to_file('my_result.txt')
def spending_by_day_week(operations: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """ Функция принимает на вход: датафрейм с транзакциями и опциональную дату,
     по умолчанию текущая дата. Функция возвращает средние траты в каждый из дней недели."""
    if date is None:
        date = pd.to_datetime(datetime.now().date())
    else:
        date = pd.to_datetime(date)
    three_months_ago = date - timedelta(days=3 * 30)  # type: ignore
    operations['Дата платежа'] = pd.to_datetime(operations['Дата платежа'], format="%d.%m.%Y", dayfirst=True)
    filtered_df = operations[(operations['Дата платежа'] >= three_months_ago) & (operations['Дата платежа'] <= date)]
    average_spending = filtered_df.groupby(filtered_df['Дата платежа'].dt.dayofweek)[
        'Сумма операции с округлением'].mean()
    return average_spending.reset_index()


@write_result_to_file('my_result.txt')
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """ Функция принимает на вход: датафрейм с транзакциями и опциональную дату,
         по умолчанию текущая дата. Функция  выводит средние траты в рабочий и в выходной день за последние 3
          месяца (от переданной даты)."""
    if date is None:
        date = pd.to_datetime(datetime.now().date())
    else:
        date = pd.to_datetime(date)
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)
    start_date = date - timedelta(days=3 * 30)  # type: ignore
    recent_transactions = transactions[(transactions['Дата операции'] >= start_date)
                                       & (transactions['Дата операции'] <= date)]

    weekdays_transactions = recent_transactions[recent_transactions['Дата операции'].dt.weekday < 5]
    weekends_transactions = recent_transactions[recent_transactions['Дата операции'].dt.weekday >= 5]

    average_spending_weekdays = weekdays_transactions['Сумма операции с округлением'].mean()
    average_spending_weekends = weekends_transactions['Сумма операции с округлением'].mean()

    # Создаем датафрейм с результатами
    result_df = pd.DataFrame({'Средние траты': [average_spending_weekdays, average_spending_weekends]},
                             index=['Рабочий день', 'Выходной день'])

    return result_df
