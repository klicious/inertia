from constants import *
from datetime import datetime
from stock_intensive_tracker.stock_summary import StockSummary
import os
import pandas as pd


def parse():
    filename = os.path.join(INPUT_DIRECTORY, 'intensive tracker.xlsx')
    stock_summaries = list()
    print(f'parsing commencing...')
    xls = pd.ExcelFile(filename)
    vols = parse_sheet(xls, sheet_name='Vol')
    pxs = parse_sheet(xls, sheet_name='Px')
    perfs = parse_sheet(xls, sheet_name='Perf')
    trades = parse_sheet(xls, sheet_name='Trade')
    print(f'parsing complete.')
    dates = set()
    stock_codes = set()
    for key in vols:
        d = key.split('|')
        stock_code = str(d[0])
        if stock_code.isnumeric():
            stock_codes.add(stock_code)
        date_str = d[1]
        if date_str != 'default':
            date = datetime.strptime(date_str, '%Y-%m-%d')
            dates.add(date)
    print(f'stock codes[{len(stock_codes)}] and dates[{len(dates)}] extracted')
    for stock_code in stock_codes:
        for date in dates:
            date_str = datetime.strftime(date, '%Y-%m-%d')
            key = f'{stock_code}|{date_str}'
            volume = vols.get(key)
            px = pxs.get(key)
            perf = perfs.get(key)
            trade = trades.get(key)
            stock_summary = StockSummary(stock_code=stock_code, date=date, volume=volume, price=px, performance=perf, trade=trade)
            stock_summaries.append(stock_summary)

    return stock_summaries


def parse_sheet(filename, sheet_name) -> dict:
    df = pd.read_excel(filename, sheet_name=sheet_name)
    stock_codes = set()
    for col in df.columns:
        col_name = str(col)
        if col and col_name.isnumeric():
            stock_codes.add(col)

    result = dict()
    for index, row in df.iterrows():
        timestamp = row.iloc[0]
        target_date_str = 'default'
        if isinstance(timestamp, datetime):
            target_date_str = timestamp.strftime('%Y-%m-%d')
        for col in stock_codes:
            value = row.get(str(col))
            if not pd.isnull(value):
                key = f'{col}|{target_date_str}'
                result[key] = value
    return result


def extract_value_from_series(row: pd.Series, column_name):
    return row[column_name]


summaries = parse()

for summary in summaries:
    print(summary)
