import pandas as pd
import numpy as np
from loguru import logger
from data_handler import get_data, get_names
from parser_ import Parser
from selenium import webdriver

MAX_LOTS_ON_PAGE = {
    'christies': 20,
    'phillips': 120,
}

FILE_NAME = 'data'
FILE_KWARGS = {
    'sep': ';',
}


def get_num_pages_and_links(row: pd.Series, parser: Parser) -> pd.Series:
    url = parser.get_url_by_name(row['split_name'])
    loaded_all, loaded = parser.load_page(url, elements=['results_elements', 'lot_elements'])
    if loaded['results_elements']['loaded']:
        num_results = parser.get_num_results()
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE[parser.auction] + 1
        row['num_pages'] = num_pages
    if loaded['lot_elements']['loaded']:
        row['links'] = parser.get_links()

    return row


def run(parser: Parser):
    data = get_names()
    data = data.apply(lambda x: get_num_pages_and_links(x, parser) if x['num_pages'] == -1 else x,
                      axis=1).reset_index(drop=True)

    data = data.explode('links')

    data.to_csv(f'students_data_{parser.auction}.csv')


def get_num_pages(row: pd.Series, parser: Parser) -> pd.Series:
    url = parser.get_url_by_name(row['split_name'])
    loaded_all, loaded = parser.load_page(url, elements=['results_elements'])

    if loaded['results_elements']['loaded']:
        num_results = parser.get_num_results()
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE[parser.auction] + 1
        row['num_pages'] = num_pages
        row['page'] = [i for i in range(1, num_pages + 1)]

    return row


def not_for_students_(parser: Parser, autosave: int = 100):
    data = get_data(f'{FILE_NAME}_{parser.auction}.csv', FILE_KWARGS)
    data = data.apply(lambda x: get_num_pages(x, parser) if x['num_pages'] == -1 else x,
                      axis=1).reset_index(drop=True)

    data = data.explode('page')
    data.to_csv(f'{FILE_NAME}_{parser.auction}.csv', **FILE_KWARGS)
    for n, (i, row) in enumerate(data.iterrows()):
        if row['links'] == ['No'] and not np.isnan(row['page']):
            url = parser.get_url_by_name(row['split_name'], page=int(row['page']))
            logger.debug(f'Collecting lots for url: {url}')
            loaded_all, loaded = parser.load_page(url, elements=['lot_elements'])

            if loaded['lot_elements']['details']['lot_box'] and loaded['lot_elements']['details']['lot_link']:
                row['links'].remove('No')
                row['links'].extend(parser.get_links())

        if (n + 1) % autosave == 0:
            logger.warning('Writing data')
            data.to_csv(f'{FILE_NAME}_{parser.auction}.csv', **FILE_KWARGS)
    logger.warning('Writing data')
    data.to_csv(f'{FILE_NAME}_{parser.auction}.csv', **FILE_KWARGS)

    data = data.explode(column=['links']).reset_index(drop=True)

    data.to_csv(f'{FILE_NAME}_{parser.auction}.csv', **FILE_KWARGS)


if __name__ == '__main__':
    parser = Parser()

    parser.set_auction('phillips')
    # run(parser)
    not_for_students_(parser, 10)

    parser.set_auction('christies')
    run(parser)
    not_for_students_(parser)

    parser.driver.close()
