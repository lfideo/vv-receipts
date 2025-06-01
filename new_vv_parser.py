import sys
import os
import pandas as pd
import re

sys.path.append('/Users/lfideo/Python/scripts/gsheets')
from google_sheet_client import GoogleSheetClient # type: ignore

gs = GoogleSheetClient('/Users/lfideo/Downloads/personal/projects/receipts/gmail_config.json')

df = gs.get_worksheet('gmail_messages', 'vkusvill')[['description', 'shop']]

numeric_pattern = re.compile(
    r"^\s*\d+\.\s*(?P<product>.+?)\s*,?\s*шт\s+(?P<price>[\d\.,]+)\s+(?P<quantity>[\d\.,]+)\s+(?P<total>[\d\.,]+)",
    re.MULTILINE | re.IGNORECASE
)

item_pattern = re.compile(
    r"\*(?P<product>[^*]+)\*\s*"            # между звёздочками — название
    r"(?P<quantity>[\d.,]+)\s*[Xx]\s*"      # количество
    r"(?P<price>[\d.,]+)"                   # цена
    r"(?:[\s\S]*?)"                         # пропустить любые строки до итоговой суммы
    r"^\=\s*(?P<total>[\d.,]+)",            # итог после строки, начинающейся с '='
    re.MULTILINE
)

parsed_rows = []
for desc in df['description'].astype(str):
    # 1. Парсим дату в каждой строке
    date_match = re.search(
        r'ДАТА ВЫДАЧИ\s*\r?\n\s*(\d{2}\.\d{2}\.\d{2})\s*(\d{2}:\d{2})',
        desc
    )
    if date_match:
        d, t = date_match.group(1), date_match.group(2)
        day, month, year = d.split('.')
        iso_dt = f"20{year}-{month}-{day} {t}"
    else:
        m2 = re.search(r'(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2})', desc)
        if m2:
            d2, t2 = m2.group(1), m2.group(2)
            day2, month2, year2 = d2.split('.')
            iso_dt = f"{year2}-{month2}-{day2} {t2}"
        else:
            # в случае если дата в чеке такого формата "03.10.21"
            m3 = re.search(r'(\d{2}\.\d{2}\.\d{2})(?!\d)', desc)
            if m3:
                d3 = m3.group(1)
                day3, month3, year3 = d3.split('.')
                iso_dt = f"20{year3}-{month3}-{day3}"
            else:
                iso_dt = None

    # 2. Парсим товары одиночной регексп-воронкой на каждую строку
    for m in item_pattern.finditer(desc):
        parsed_rows.append({
            "date": iso_dt,
            "product": m.group("product").strip().lower(),
            "quantity": float(m.group("quantity").replace(",", ".")),
            "price": float(m.group("price").replace(",", ".")),
            "total_sum": float(m.group("total").replace(",", "."))
        })
    # parse numeric-list style items
    for m in numeric_pattern.finditer(desc):
        parsed_rows.append({
            "date": iso_dt,
            "product": m.group("product").strip().lower(),
            "quantity": float(m.group("quantity").replace(',', '.')),
            "price": float(m.group("price").replace(',', '.')),
            "total_sum": float(m.group("total").replace(',', '.'))
        })

parsed_df = pd.DataFrame(parsed_rows)
print(parsed_df)