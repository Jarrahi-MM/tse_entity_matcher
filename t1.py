# %%
import json

# %%
from typing import Dict, List

bourseview_symbols_details = json.load(open('./bourseview_symbols_details.json'))
# %%
map_symbol_names: Dict[List] = {}


# %%
def expand(name: str) -> str:
    name = name.replace('.', ' ')
    return name


# %%
for item in bourseview_symbols_details['items']:
    if item['symbolPouyaFa'] not in map_symbol_names:
        map_symbol_names[item['symbolPouyaFa']] = []
    map_symbol_names[item['symbolPouyaFa']].append(expand(item['isin']))
    map_symbol_names[item['symbolPouyaFa']].append(expand(item['namePouya']))
    map_symbol_names[item['symbolPouyaFa']].append(expand(item['namePouyaFa']))
