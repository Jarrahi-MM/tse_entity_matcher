# %%
import json
import re
from typing import Dict, List, Set

# %%

bourseview_symbols_details = json.load(open('./bourseview_symbols_details.json'))
# %%
map_symbol_names: Dict[str, Set[str]] = {}


# %%
def expand(name: str) -> str:
    name = name.replace('.', ' ')
    name = name.strip()
    name = re.sub('( |‌)+', '( |‌)', name)
    return name


# %%
for item in bourseview_symbols_details['items']:
    if item['symbolPouyaFa'] not in map_symbol_names:
        map_symbol_names[item['symbolPouyaFa']] = set()
    map_symbol_names[item['symbolPouyaFa']].add(expand(item['isin']))
    map_symbol_names[item['symbolPouyaFa']].add(expand(item['namePouya']))
    map_symbol_names[item['symbolPouyaFa']].add(expand(item['namePouyaFa']))
