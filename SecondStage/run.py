import pandas as pd
from utils.parser_ import AutoParser
from loguru import logger
import os

from SecondStage.data_handler import get_data

FILE_NAME = '..\\Data\\data'
FILE_KWARGS = {
    # 'sep': '@'
}
SEPARATOR = '@'


def get_details(row: pd.Series, parser: AutoParser) -> pd.Series:
    url = row['links']
    elements = ['second_stage']
    loaded_all, loaded = parser.load_page(url, elements=elements)
    if loaded_all:
        results = {}
        for element in elements:
            results.update(parser.parse_element(element))
        for key, value in results.items():
            for v in value:
                if 'sep' in FILE_KWARGS and FILE_KWARGS['sep'] in v:
                    logger.error(f'Separator ({FILE_KWARGS["sep"]}) was found in value:\n {v}')
                    raise NameError('Separator was found in value')
                if SEPARATOR in v:
                    logger.error(f'Separator ({SEPARATOR}) was found in value:\n {v}')
                    raise NameError('Separator was found in value')
            row[key] = SEPARATOR.join(value)

    return row


def run(parser: AutoParser):
    data = get_data(f'{FILE_NAME}_{parser.auction}.csv', FILE_KWARGS)
    # data = data.loc[data['name'] == 'Pablo Picasso']
    data = data.loc[data['name'] == 'Adolf von Menzel']
    # data = data.loc[data['name'] == 'Joan Mitchell']

    data = data.apply(lambda x: get_details(x, parser), axis=1).reset_index(drop=True)

    data.to_csv(f'{FILE_NAME}_{parser.auction}_students_test_.csv', **FILE_KWARGS)


if __name__ == '__main__':
    parser = AutoParser('christies')
    # parser = AutoParser('phillips')
    run(parser)
    parser.driver.close()

    '''parser = PhillipsParser()
    run(parser)
    parser.driver.close()'''
