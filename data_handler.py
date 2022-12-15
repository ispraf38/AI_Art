import pandas as pd
from typing import Any, Dict, Optional, List

'''with open('arts2.csv', 'r') as f:
    data = f.read()

data = data.replace(';', '@')
data = data.replace('@ ', '; ')

with open('prehandled_data.csv', 'w') as f:
    f.write(data)'''


def get_names(file_name: str = 'prehandled_data.csv', file_kwargs: Optional[Dict[str, Any]] = None) -> List[str]:
    if file_kwargs is None:
        file_kwargs = {
            'sep': '@',
            'names': ['name', 'col2', 'col3', 'col4']
        }
    data = pd.read_csv(file_name, **file_kwargs)
    names = set(data['name'].to_list())
    handled_names = []
    for n in names:
        if type(n) == str:
            handled_names.extend(n.split('--'))
    return handled_names