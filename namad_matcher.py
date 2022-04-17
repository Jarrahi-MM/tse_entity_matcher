# %%
import json
import re
from typing import Dict, List, Set
from parsi_io.modules.number_extractor import NumberExtractor

# %%
bourseview_symbols_details = json.load(
    open('./bourseview_symbols_details.json'))
map_symbol_names: Dict[str, Set[str]] = {}

# %%


def expand_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'( |‌|\(|\)|-|_|ـ|\.)+', r'(| |‌|\(|\)|-|_|ـ|\.)+', name)
    return name


def expand_term(term: str) -> str:
    term = re.sub(r'#عدد', r'~+', term)
    term = re.sub(r'؟', r'\?', term)
    term = term.strip()
    term = re.sub(r'( |‌|\(|\)|-|_|ـ|\.)+', r'(| |‌|\(|\)|-|_|ـ|\.)+', term)
    return term


def tag_numbers(original_text: str) -> str:
    extractor = NumberExtractor()
    new_text = original_text
    num_list = extractor.run(original_text)
    for d in num_list:
        len = d["span"][1] - d["span"][0]
        new_text = new_text[:d["span"][0]]+'~'*(len)+new_text[d["span"][1]:]
    return new_text


# %%
for item in bourseview_symbols_details['items']:
    if item['symbolPouyaFa'] not in map_symbol_names:
        map_symbol_names[item['symbolPouyaFa']] = set()
    map_symbol_names[item['symbolPouyaFa']].add(expand_name(item['isin']))
    map_symbol_names[item['symbolPouyaFa']].add(expand_name(item['namePouya']))
    map_symbol_names[item['symbolPouyaFa']].add(
        expand_name(item['namePouyaFa']))

# %%
# regex = expand('نفت ( ) -- _ـ  ‌ ها')
# test_str = 'نفتها'

# matches = re.finditer(regex, test_str, re.MULTILINE)

# for matchNum, match in enumerate(matches, start=1):
#     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
