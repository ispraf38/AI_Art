import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, List
import os

'''with open('arts2.csv', 'r') as f:
    data = f.read()

data = data.replace(';', '@')
data = data.replace('@ ', '; ')

with open('prehandled_data.csv', 'w') as f:
    f.write(data)'''


def get_data(file_name: str = 'data.csv', file_kwargs: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    if file_kwargs is None:
        file_kwargs = {
            'sep': ';',
        }

    if os.path.exists(file_name):
        data = pd.read_csv(file_name, **file_kwargs)
    else:
        data = get_names()

    return data


def get_names(file_name: str = 'prehandled_data.csv', file_kwargs: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    if file_kwargs is None:
        file_kwargs = {
            'sep': '@',
            'names': ['name', 'col2', 'col3', 'col4'],
        }
    data = pd.read_csv(file_name, **file_kwargs)
    data = data.drop(columns=['col2', 'col3', 'col4'])
    data = data.replace('', np.nan)
    data = data.groupby(by=['name'], dropna=True).first().reset_index()
    data['split_name'] = data['name'].str.split('--')
    data = data.explode('split_name').reset_index(drop=True)
    data['chr_num_pages'] = -1
    # names = set(data['name'].to_list())
    # handled_names = []
    # for n in names:
    #     if type(n) == str:
    #         handled_names.extend(n.split('--'))
    return data


if __name__ == '__main__':
    names = get_data()
    print(names)
    names.to_csv('test.csv', sep=';')
