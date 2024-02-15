import csv
import json


def transform_to_json(file_path, output_json_path):
    with open(file_path, 'r') as csv_file, open(output_json_path, 'w') as jsonl_file:
        csv_reader = csv.DictReader(csv_file)
        previous_open = None
        previous_high = None
        previous_low = None
        previous_close = None
        rows = list(csv_reader)[-8000:]
        transformed_data = []
        for row in rows:
            date = row['date']
            open_value = row['open']
            high = row['high']
            low = row['low']
            close = row['close']
            request = f"What will be open, high, low, close of BTC at the moment of {date}?\nPrevious Open: {previous_open}, Previous High: {previous_high}, Previous Low: {previous_low}, Previous Close: {previous_close}"
            response = f"Open: {open_value}, High: {high}, Low: {low}, Close: {close}.\nPrevious Open: {previous_open}, Previous High: {previous_high}, Previous Low: {previous_low}, Previous Close: {previous_close}"
            transformed_data.append({'request': request, 'response': response})
            previous_open = open_value
            previous_high = high
            previous_low = low
            previous_close = close
        json.dump(transformed_data, jsonl_file, ensure_ascii=False, indent=4)

# Пример использования
file_path = 'power_data.csv'
output_json_path = 'yandex.json'
transform_to_json(file_path, output_json_path)