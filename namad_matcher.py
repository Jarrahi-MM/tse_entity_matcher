# %%
import json
import re
from operator import itemgetter
from typing import Dict, List, Tuple
from parsi_io.modules.number_extractor import NumberExtractor
# changed pattern.py in parsi.io
import pandas as pd

# %%
bourseview_symbols_details = json.load(
    open('./bourseview_symbols_details.json'))
rahavard_symbols_details = json.load(
    open('./rahavard_symbols_details.json'))
# Tuple[regex_exp, detailed_type]
map_symbol_regexes: Dict[str, List[Tuple[str, str]]] = {}
# detailed_type is نماد شرکت or حق تقدم شرکت
events_df = pd.read_excel('./events.xlsx', engine='openpyxl')
map_event_regexes: Dict[str, List[Tuple[str, str]]] = {}
junk_words_df = pd.read_excel('./junk_words.xlsx', engine='openpyxl')['لیست بخش‌های تکراری اسامی']


# %%
W1 = r'( |‌|\(|\)|-|_|ـ|\.)'
Y_NAKARE = r'(یی|ی| ی|‌ی)'
HAGH = r'(ح|حق|تقدم|حق تقدم)'.replace(' ', f'{W1}*')


def expand_name_and_hagh(name: str) -> List[str]:
    if len(name) <= 2:
     # شکف/کف بیمه ما/ما
        return []
    return expand_persian_name(name) + expand_persian_hagh_name(name)


def expand_persian_name(name: str) -> List[str]:
    name = name.strip()
    name = re.sub(r'\*', '\*', name)
    name = re.sub(f'{W1}+', f'{Y_NAKARE}?{W1}*', name)
    for junk in junk_words_df:
        name=name.replace(f'{W1}*{junk}', f'({W1}*{junk})?')
        name=name.replace(f'{junk}{W1}*', f'({junk}{W1}*)?')
    return [(re.compile(f'\\b{name}{Y_NAKARE}?\\b'), 'نماد شرکت')]


def expand_persian_hagh_name(name: str) -> List[str]:
    name = name.strip()
    name = re.sub(r'\*', '\*', name)
    name = re.sub(f'{W1}+', f'{Y_NAKARE}?{W1}*', name)
    for junk in junk_words_df:
        name=name.replace(f'{W1}*{junk}', f'({W1}*{junk})?')
        name=name.replace(f'{junk}{W1}*', f'({junk}{W1}*)?')
    return [(re.compile(f'\\b{HAGH}{W1}*{name}{Y_NAKARE}?\\b'), 'نماد حق تقدم شرکت'),
            (re.compile(f'\\b{name}{Y_NAKARE}?{W1}*{HAGH}\\b'), 'نماد حق تقدم شرکت')]


def expand_term(term: str) -> List[str]:
    term = re.sub(r'#NUM', r'(~+)', term)
    term = re.sub(r'؟', r'?', term)
    term = term.strip()
    term = re.sub(r'( |‌)+', f'{Y_NAKARE}?{W1}*', term)
    return [(re.compile(f'{term}{Y_NAKARE}?'), 'اصطلاح')]  # TODO add \\b


def tag_numbers(original_text: str) -> str:
    extractor = NumberExtractor()
    new_text = original_text
    num_list = extractor.run(original_text)
    for d in num_list:
        len = d["span"][1] - d["span"][0]
        new_text = new_text[:d["span"][0]] + '~' * \
            (len) + new_text[d["span"][1]:]  # can be more efficient
    return new_text


# %%
for item in bourseview_symbols_details['items']:
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

for item in rahavard_symbols_details['asset_data_list']:
    i = item['asset']
    if i['trade_symbol'] not in map_symbol_regexes:
        map_symbol_regexes[i['trade_symbol']] = []
    map_symbol_regexes[i['trade_symbol']].extend(
        expand_name_and_hagh(i['name']))
    map_symbol_regexes[i['trade_symbol']].extend(
        expand_name_and_hagh(i['short_name']))
    map_symbol_regexes[i['trade_symbol']].extend(
        expand_name_and_hagh(i['trade_symbol']))
    # may be duplicate ...

map_symbol_regexes['فراکاب'] = []
map_symbol_regexes['فراکاب'].extend(expand_name_and_hagh('فراکاب'))

map_symbol_regexes['انرژی3'].extend(expand_name_and_hagh('انرژی 3'))
map_symbol_regexes['انرژی3'].extend(expand_name_and_hagh('انرژی ۳'))

map_symbol_regexes['انرژی2'].extend(expand_name_and_hagh('انرژی 2'))
map_symbol_regexes['انرژی2'].extend(expand_name_and_hagh('انرژی ۲'))

map_symbol_regexes['انرژی1'].extend(expand_name_and_hagh('انرژی 1'))
map_symbol_regexes['انرژی1'].extend(expand_name_and_hagh('انرژی ۱'))

# %%
for index, row in events_df.iterrows():
    if row['نوع اصطلاح'] not in map_event_regexes:
        map_event_regexes[row['نوع اصطلاح']] = []
    map_event_regexes[row['نوع اصطلاح']].extend(expand_term(row['رجکس اصلاح']))

# %%


def find(text: str) -> List[Dict]:
    tagged_text = tag_numbers(text)
    out = []
    for key in map_event_regexes.keys():
        regexes = map_event_regexes[key]
        for r in regexes:
            for match in r[0].finditer(tagged_text):
                out.append(
                    {"type": key, "marker": text[match.start(): match.end()], "span": match.span()})
    for key in map_symbol_regexes.keys():
        regexes = map_symbol_regexes[key]
        for r in regexes:
            # don't use tagged text. for example انرژی3
            for match in r[0].finditer(text):
                out.append({"type": "نماد", "type_detailed": r[1], "symbol": key, "marker": text[match.start(
                ): match.end()], "span": match.span()})
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
    dict_list = find(text)
    print(dict_list)


