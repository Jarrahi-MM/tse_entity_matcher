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
rahavard_symbols_details = json.load(
    open('./rahavard_symbols_details.json'))
map_symbol_names: Dict[str, List[str]] = {}
events_df = pd.read_excel('./events.xlsx', engine='openpyxl')
events_dict: Dict[str, List[str]] = {}


# %%
W1=r'( |‌|\(|\)|-|_|ـ|\.)'
Y_NAKARE=r'(یی|ی| ی|‌ی)'
HAGH=r'(ح|حق|تقدم|حق تقدم)'.replace(' ', f'{W1}*')

def expand_persian_name(name: str) -> List[str]:
    name = name.strip()
    name = re.sub(r'\*', '\*', name)
    name = re.sub(f'{W1}+', f'{Y_NAKARE}?{W1}*', name)
    return ['\\b' + name + '\\b']

def expand_persian_hagh_name(name: str) -> List[str]:
    x=f'(ح|حق|تقدم|حق{W1}+تقدم||)'
    name = name.strip()
    name = re.sub(r'\*', '\*', name)
    name = re.sub(f'{W1}+', f'{Y_NAKARE}?{W1}*', name)
    return ['\\b' + name + '\\b']


def expand_term(term: str) -> List[str]:
    term = re.sub(r'#NUM', r'(~+)', term)
    term = re.sub(r'؟', r'?', term)
    term = term.strip()
    term = re.sub(r'( |‌)+', r'(| |‌|\(|\)|-|_|ـ|\.)+', term)
    return [term]  # TODO add \\b


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
    map_symbol_names[item['symbolPouyaFa']].extend(
        expand_persian_name(item['isin']))
    map_symbol_names[item['symbolPouyaFa']].extend(
        expand_persian_name(item['namePouya']))
    map_symbol_names[item['symbolPouyaFa']].extend(
        expand_persian_name(item['namePouyaFa']))
    map_symbol_names[item['symbolPouyaFa']].extend(
        expand_persian_name(item['symbolPouyaFa']))

for item in rahavard_symbols_details['asset_data_list']:
    i = item['asset']
    if i['trade_symbol'] not in map_symbol_names:
        map_symbol_names[i['trade_symbol']] = []
    map_symbol_names[i['trade_symbol']].extend(expand_persian_name(i['name']))
    map_symbol_names[i['trade_symbol']].extend(
        expand_persian_name(i['short_name']))
    map_symbol_names[i['trade_symbol']].extend(
        expand_persian_name(i['trade_symbol']))
    # may be duplicate ...

map_symbol_names['انرژی3'].extend(expand_persian_name('انرژی 3'))
map_symbol_names['انرژی3'].extend(expand_persian_name('انرژی ۳'))

map_symbol_names['انرژی2'].extend(expand_persian_name('انرژی 2'))
map_symbol_names['انرژی2'].extend(expand_persian_name('انرژی ۲'))

map_symbol_names['انرژی1'].extend(expand_persian_name('انرژی 1'))
map_symbol_names['انرژی1'].extend(expand_persian_name('انرژی ۱'))

# %%
for index, row in events_df.iterrows():
    if row['نوع اصطلاح'] not in events_dict:
        events_dict[row['نوع اصطلاح']] = []
    events_dict[row['نوع اصطلاح']].extend(expand_term(row['رجکس اصلاح']))

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
            # don't use tagged text. انرژی3
            matches = re.finditer(r, text, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                out.append({"type": "نماد شرکت بورس", "symbol": key, "marker": text[match.start(
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



# Todo haghtaghaddom
# Todo inke setaii haro dotaii mishe nevesht -> loghate bi arzesh
# run("نفت قشم سهم خیلی خوبیه")

