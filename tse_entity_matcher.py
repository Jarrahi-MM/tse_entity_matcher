# %%
import json
import re
from operator import itemgetter
from typing import Dict, List, Tuple, Pattern
from parsi_io.modules.number_extractor import NumberExtractor  # changed pattern.py in parsi.io
import pandas as pd
import tqdm

# %% Read Data-sets
bourseview_symbols_details = json.load(
    open('data/bourseview_symbols_details.json'))
rahavard_symbols_details = json.load(
    open('data/rahavard_symbols_details.json'))
# Tuple[regex_exp, detailed_type]       detailed_type is نماد شرکت or حق تقدم شرکت
map_symbol_regexes: Dict[str, List[Tuple[Pattern[str], str]]] = {}
events_df = pd.read_excel('data/events.xlsx', engine='openpyxl')
map_event_regexes: Dict[str, List[Tuple[Pattern[str], str]]] = {}
junk_words_df = pd.read_excel('data/junk_words.xlsx', engine='openpyxl')['لیست بخش‌های تکراری اسامی']

# %%
W1 = r'( |‌|\(|\)|-|_|ـ|\.)'  # کاربران ممکن است به جای فاصله مثلا از ـ استفاده کنند.
W2 = r'( |‌)'
Y_NAKARE = r'(یی|ی| ی|‌ی)'  # نوشتن فولاد مبارکه اصفهان یا فولاد مبارکه‌ی اصفهان
HAGH = r'(ح|حق|تقدم|حق تقدم)'.replace(' ', f'{W1}*')  # پشتیبانی از حق‌تقدم‌ها مانند «فولادح» یا «حق‌تقدم فولاد» یا ...


# این تابع برای توسعه‌ی نام‌ها و نمادهای بورسی است تا فرم‌های مختلف را در بگیرند.
def expand_name_and_hagh(name: str) -> List[Tuple[Pattern[str], str]]:
    if len(name) <= 2:
        # نادیده گرفتن نمادهای ۲ حرفی به دلیل مشکلاتی که ایجاد می‌کنند.
        # شکف/کف بیمه ما/ما
        return []
    return expand_persian_name(name) + expand_persian_hagh_name(name)


# توسعه‌ی نام‌ها و نمادهای بورسی
def expand_persian_name(name: str) -> List[Tuple[Pattern[str], str]]:
    name = name.strip()
    name = re.sub(r'\*', '\\*', name)
    name = re.sub(f'{W1}+', f'{Y_NAKARE}?{W1}*', name)
    for junk in junk_words_df:
        name = name.replace(f'{W1}*{junk}', f'({W1}*{junk})?')
        name = name.replace(f'{junk}{W1}*', f'({junk}{W1}*)?')
    return [(re.compile(f'\\b{name}{Y_NAKARE}?\\b'), 'نماد شرکت')]


# توسعه‌ی حق‌تقدم نام‌ها و نمادهای بورسی
def expand_persian_hagh_name(name: str) -> List[Tuple[Pattern[str], str]]:
    name = name.strip()
    name = re.sub(r'\*', '\\*', name)
    name = re.sub(f'{W1}+', f'{Y_NAKARE}?{W1}*', name)
    for junk in junk_words_df:
        name = name.replace(f'{W1}*{junk}', f'({W1}*{junk})?')
        name = name.replace(f'{junk}{W1}*', f'({junk}{W1}*)?')
    return [(re.compile(f'\\b{HAGH}{W1}*{name}{Y_NAKARE}?\\b'), 'نماد حق تقدم شرکت'),
            (re.compile(f'\\b{name}{Y_NAKARE}?{W1}*{HAGH}\\b'), 'نماد حق تقدم شرکت')]


# این تابع برای توسعه‌ی اصطلاحات بورسی است تا فرم‌های مختلف را در بگیرند.
# در اینجا #NUM معرف عدد است.
# آن را با ~ جایگزین می‌کنیم. در متن ورودی نیز اعداد را به کمک کتاب‌خانه‌ی parsi با ~ جایگزین خواهیم کرد تا مچ شوند.
def expand_term(term: str) -> List[Tuple[Pattern[str], str]]:
    term = re.sub(r'#NUM', r'(~+)', term)
    term = re.sub(r'؟', r'?', term)  # در اکسل، ممکن است از علامت سوال فارسی در عبارات منظم استفاده شده باشد.
    term = term.strip()
    term = re.sub(f'{W2}+', f'{Y_NAKARE}?{W1}*', term)
    return [(re.compile(f'{term}{Y_NAKARE}?'), 'اصطلاح')]  # may add \\b?


# استفاده از کتاب‌خانه برای جایگزین کردن اعداد با ~ تا با عبارات منظم ساخته شده قابل تطبیق باشند.
def tag_numbers(original_text: str) -> str:
    extractor = NumberExtractor()
    new_text = original_text
    num_list = extractor.run(original_text)
    for d in num_list:
        length = d["span"][1] - d["span"][0]
        new_text = new_text[:d["span"][0]] + '~' * length + new_text[d["span"][1]:]
    return new_text


# %%
for item in tqdm.tqdm(bourseview_symbols_details['items']):
    if item['symbolPouyaFa'] not in map_symbol_regexes:
        map_symbol_regexes[item['symbolPouyaFa']] = []
    map_symbol_regexes[item['symbolPouyaFa']].extend(
        expand_name_and_hagh(item['isin']))
    map_symbol_regexes[item['symbolPouyaFa']].extend(
        expand_name_and_hagh(item['namePouya']))
    map_symbol_regexes[item['symbolPouyaFa']].extend(
        expand_name_and_hagh(item['namePouyaFa']))
    map_symbol_regexes[item['symbolPouyaFa']].extend(
        expand_name_and_hagh(item['symbolPouyaFa']))

for item in tqdm.tqdm(rahavard_symbols_details['asset_data_list']):
    asset = item['asset']
    if asset['trade_symbol'] not in map_symbol_regexes:
        map_symbol_regexes[asset['trade_symbol']] = []
    map_symbol_regexes[asset['trade_symbol']].extend(
        expand_name_and_hagh(asset['name']))
    map_symbol_regexes[asset['trade_symbol']].extend(
        expand_name_and_hagh(asset['short_name']))
    map_symbol_regexes[asset['trade_symbol']].extend(
        expand_name_and_hagh(asset['trade_symbol']))
    # may be duplicate ...

# اضافه کردن برخی اسامی که در دیتاست نبودند.
map_symbol_regexes['فراکاب'] = []
map_symbol_regexes['فراکاب'].extend(expand_name_and_hagh('فراکاب'))

map_symbol_regexes['انرژی3'].extend(expand_name_and_hagh('انرژی 3'))
map_symbol_regexes['انرژی3'].extend(expand_name_and_hagh('انرژی ۳'))

map_symbol_regexes['انرژی2'].extend(expand_name_and_hagh('انرژی 2'))
map_symbol_regexes['انرژی2'].extend(expand_name_and_hagh('انرژی ۲'))

map_symbol_regexes['انرژی1'].extend(expand_name_and_hagh('انرژی 1'))
map_symbol_regexes['انرژی1'].extend(expand_name_and_hagh('انرژی ۱'))

# %%
for index, row in tqdm.tqdm(events_df.iterrows()):
    if row['نوع اصطلاح'] not in map_event_regexes:
        map_event_regexes[row['نوع اصطلاح']] = []
    map_event_regexes[row['نوع اصطلاح']].extend(expand_term(row['رجکس اصلاح']))


# %%


def find_entities(text: str) -> List[Dict]:
    # جایگزین کردن اعداد با ~
    tagged_text = tag_numbers(text)
    out = []
    # در اصطلاحات ممکن است عدد داشته باشیم. پس باید از tagged_text استفاده کنیم و پس از کشف اسپن‌ها، مارکر را از روی
    # متن اولیه کشف کنیم.
    for key in map_event_regexes.keys():
        regexes = map_event_regexes[key]
        for r in regexes:
            for match in r[0].finditer(tagged_text):
                out.append(
                    {"type": key, "marker": text[match.start(): match.end()], "span": match.span()})
    # از آنجا که در نماد‌ها و نام‌های بورسی عدد به طور عمومی نداریم و صرفا برخی اعداد خاص مانند انرژی3 داریم، باید از
    # متن اصلی استفاده کنیم.
    for key in map_symbol_regexes.keys():
        regexes = map_symbol_regexes[key]
        for r in regexes:
            for match in r[0].finditer(text):
                out.append({"type": "نماد", "type_detailed": r[1], "symbol": key, "marker": text[match.start(
                ): match.end()], "span": match.span()})
    # حذف موجودیت‌های کشف شده‌ای که زیرمجموعه‌ی یک موجودیت کشف شده‌ی دیگر هستند.
    dict_list = remove_complete_overlaps(out)
    return dict_list


def check_overlap(s1, s2):
    return "SECOND_LONGER" if (s1[0] == s2[0]) else ("FIRST_LONGER" if s2[1] <= s1[1] else "NO_COMPLETE_OVERLAP")


def remove_complete_overlaps(dict_list: List[Dict]) -> List[Dict]:
    if len(dict_list) == 0:
        return dict_list
    dict_list = sorted(dict_list, key=itemgetter('span'))
    prev_span = dict_list[0]['span']
    useless_indexes = []
    for i in range(1, len(dict_list)):
        cur_span = dict_list[i]['span']
        overlap_type = check_overlap(prev_span, cur_span)
        if overlap_type == "NO_COMPLETE_OVERLAP":
            prev_span = cur_span
        elif overlap_type == "SECOND_LONGER":
            useless_indexes.append(i - 1)
            prev_span = cur_span
        elif overlap_type == "FIRST_LONGER":
            useless_indexes.append(i)
    for i in reversed(useless_indexes):
        del dict_list[i]
    return dict_list


def run(text: str):
    dict_list = find_entities(text)
    print(json.dumps(dict_list, indent=4, ensure_ascii=False).encode('utf8').decode())
