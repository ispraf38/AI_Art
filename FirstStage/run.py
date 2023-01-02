import pandas as pd
from FirstStage.data_handler import get_names
from utils.parser_ import ChristiesParser, PhillipsParser
from typing import Union

MAX_LOTS_ON_PAGE = {
    'christies': 20,
    'phillips': 120,
}

FILE_NAME = '..\\Data\\data'
FILE_KWARGS = {
    'sep': ';',
}


def get_num_pages_and_links(row: pd.Series, parser: Union[ChristiesParser, PhillipsParser]) -> pd.Series:
    url = parser.get_url_by_name(row['split_name'])
    loaded_all, loaded = parser.load_page(url, elements=['results_elements', 'lot_elements'])
    if loaded['results_elements']['loaded']:
        num_results = parser.get_num_results()
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE[parser.auction] + 1
        row['num_pages'] = num_pages
    if loaded['lot_elements']['details']['lot_box'] and loaded['lot_elements']['details']['lot_link']:
        row['links'] = parser.get_links()

    return row


def run(parser: Union[ChristiesParser, PhillipsParser]):
    data = get_names()
    data = data.apply(lambda x: get_num_pages_and_links(x, parser) if x['num_pages'] == -1 else x,
                      axis=1).reset_index(drop=True)

    data = data.explode('links')

    data.to_csv(f'{FILE_NAME}_{parser.auction}_students.csv')


if __name__ == '__main__':
    parser = ChristiesParser()
    run(parser)
    parser.driver.close()

    parser = PhillipsParser()
    # run(parser)
    parser.driver.close()
