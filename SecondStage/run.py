import pandas as pd
from utils.parser_ import AutoParser
from loguru import logger
import os

from SecondStage.data_handler import get_data

MAX_LOTS_ON_PAGE = {
    'christies': 20,
    'phillips': 120,
}

FILE_NAME = '..\\Data\\data'
FILE_KWARGS = {
    'sep': '@'
}


def get_details(row: pd.Series, parser: AutoParser) -> pd.Series:
    url = row['links']
    elements = ['name_price']
    if parser.auction == 'christies':
        elements.append('description')
    if parser.auction == 'phillips':
        elements.append('image')
    loaded_all, loaded = parser.load_page(url, elements=elements)
    if loaded_all:
        results = {}
        for element in elements:
            results.update(parser.parse_element(element))
        for key, value in results.items():
            if 'sep' in FILE_KWARGS:
                if FILE_KWARGS['sep'] in value[0]:
                    logger.error(f'Separator ({FILE_KWARGS["sep"]}) was found in value:\n {value[0]}')
                    raise NameError('Separator was found in value')
            row[key] = value[0]

    return row


def run(parser: AutoParser):
    data = get_data(f'{FILE_NAME}_{parser.auction}.csv', FILE_KWARGS)
    data = data.loc[data['name'] == 'Pablo Picasso']

    data = data.apply(lambda x: get_details(x, parser), axis=1).reset_index(drop=True)

    data.to_csv(f'{FILE_NAME}_{parser.auction}_students_2.csv', sep=FILE_KWARGS['sep'])


if __name__ == '__main__':
    # parser = AutoParser('christies')
    parser = AutoParser('phillips')
    run(parser)
    parser.driver.close()

    '''parser = PhillipsParser()
    run(parser)
    parser.driver.close()'''
