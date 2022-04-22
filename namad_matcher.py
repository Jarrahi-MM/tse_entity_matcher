# %%
import json
import re
from operator import itemgetter
from typing import Dict, List
from parsi_io.modules.number_extractor import NumberExtractor
# changed pattern.py in parsi.io
import pandas as pd

# %%
bourseview_symbols_details = json.load(
    open('./bourseview_symbols_details.json'))
map_symbol_names: Dict[str, List[str]] = {}
events_df = pd.read_excel('./events.xlsx', engine='openpyxl')
events_dict: Dict[str, List[str]] = {}


# %%
def expand_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'\*', '\*', name)
    name = re.sub(r'( |‌|\(|\)|-|_|ـ|\.)+', r'(| |‌|\(|\)|-|_|ـ|\.)+', name)
    return '\\b' + name + '\\b'


def expand_term(term: str) -> str:
    term = re.sub(r'#NUM', r'(~+)', term)
    term = re.sub(r'؟', r'?', term)
    term = term.strip()
    term = re.sub(r'( |‌)+', r'(| |‌|\(|\)|-|_|ـ|\.)+', term)
    return term  # TODO add \\b


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
    if item['symbolPouyaFa'] not in map_symbol_names:
        map_symbol_names[item['symbolPouyaFa']] = []
    map_symbol_names[item['symbolPouyaFa']].append(expand_name(item['isin']))
    map_symbol_names[item['symbolPouyaFa']].append(
        expand_name(item['namePouya']))
    map_symbol_names[item['symbolPouyaFa']].append(
        expand_name(item['namePouyaFa']))
    map_symbol_names[item['symbolPouyaFa']].append(
        expand_name(item['symbolPouyaFa']))
# %%
for index, row in events_df.iterrows():
    if row['نوع اصطلاح'] not in events_dict:
        events_dict[row['نوع اصطلاح']] = []
    events_dict[row['نوع اصطلاح']].append(expand_term(row['رجکس اصلاح']))

# %%


def find(text: str) -> List[Dict]:
    tagged_text = tag_numbers(text)
    out = []
    for key in events_dict.keys():
        regexes = events_dict[key]
        for r in regexes:
            matches = re.finditer(r, tagged_text, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                out.append(
                    {"type": key, "marker": text[match.start(): match.end()], "span": match.span()})
    for key in map_symbol_names.keys():
        # search_pattern = r'(?:\W|^)' + f'(' + key + ')' + r'(?:\W|$)'
        # for match in re.compile(search_pattern).finditer(tagged_text):
        #     _span_b, _span_e = match.span(1)
        #     out.append({"type": "نماد", "marker": text[_span_b: _span_e], "span": match.span(1)})
        regexes = map_symbol_names[key]
        for r in regexes:
            matches = re.finditer(r, tagged_text, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                out.append({"type": "نماد شرکت بورس", "symbol": key, "marker": text[match.start(
                ): match.end()], "span": match.span()})
    dict_list = remove_complete_overlaps(out)
    return dict_list


def check_overlap(s1, s2):
    return "SECOND_LONGER" if (s1[0] == s2[0]) else ("FIRST_LONGER" if s2[1] <= s1[1] else "NO_COMPLETE_OVERLAP")


def remove_complete_overlaps(dict_list: List[Dict]) -> List[Dict]:
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


# run("فولاد مبارکه‌ی اصفهان")
# run("فولاد مبارکه اصفهان")
# run('جریان آغاز معاملات فزر با ۱۵.۲ واحد تاثیر مثبت بر روند صعودی بازار فرابورس اثر گذار بود.')
# run('برکت همین افشای ب باعث شد سهم سه درصد مثبت شود. به خاطر همین میگم پیگیر باشید.')
# run('گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰/۰۹/۳۰ برای دیران منتشر شد.')
# Todo haghtaghaddom
# Todo inke setaii haro dotaii mishe nevesht -> loghate bi arzesh
# run("نفت قشم سهم خیلی خوبیه")
