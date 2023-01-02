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


def run(parser: AutoParser, autosave: int = 100):
    tmp_name = f'{FILE_NAME}_{parser.auction}_tmp.csv'
    data = get_data(f'{FILE_NAME}_{parser.auction}_students.csv', tmp_name, FILE_KWARGS)

    data.to_csv(tmp_name, **FILE_KWARGS)
    for n, (i, row) in enumerate(data.iterrows()):
        if not row['handled']:
            url = row['links']
            loaded_all, loaded = parser.load_page(url, elements=['name_price', 'description'])
            if loaded_all:
                description = parser.parse_element('description')
                name_price = parser.parse_element('name_price')
                for key, value in (description | name_price).items():
                    if 'sep' in FILE_KWARGS:
                        if FILE_KWARGS['sep'] in value[0]:
                            logger.error(f'Separator ({FILE_KWARGS["sep"]}) was found in value:\n {value[0]}')
                            raise NameError('Separator was found in value')
                    row[key].remove('~')
                    row[key].extend(value)
                row['handled'] = True

            if (n + 1) % autosave == 0:
                logger.warning('Writing data')
                data.to_csv(tmp_name, **FILE_KWARGS)

    data.to_csv(f'{FILE_NAME}_{parser.auction}_students_2.csv')


if __name__ == '__main__':
    parser = AutoParser('christies')
    run(parser, autosave=10)
    parser.driver.close()

    '''parser = PhillipsParser()
    run(parser)
    parser.driver.close()'''
