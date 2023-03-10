import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, List
from loguru import logger
import os


def get_data(file_name: str,
             file_kwargs: Optional[Dict[str, Any]] = None,
             tmp_name: Optional[str] = None) -> pd.DataFrame:
    if file_kwargs is None:
        file_kwargs = {}

    if tmp_name is not None and os.path.exists(tmp_name):
        logger.info(f'File {tmp_name} was found')
        data = pd.read_csv(tmp_name, index_col=0, **file_kwargs)
    elif os.path.exists(file_name):
        logger.info(f'File {file_name} was found')
        data = pd.read_csv(file_name, index_col=0)
        data = data.loc[data['links'] != 'No']
        data = data.loc[~data['links'].str.contains('onlineonly')]
        data = data.groupby('links').first().reset_index()
    else:
        logger.error(f'File {file_name} was not found')
        data = pd.DataFrame()
        return data


    return data


if __name__ == '__main__':
    names = get_data('test.csv')
    print(names)
    names.to_csv('test.csv', sep=';')
