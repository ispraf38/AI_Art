import pandas as pd
import numpy as np
from loguru import logger
from data_handler import get_data, get_names
from christies.parser_ import get_url_by_name, get_soup_by_url, get_num_results_bs, get_links_bs
from christies.parser_ import LOT_ELEMENTS, RESULTS_ELEMENTS
from selenium import webdriver

MAX_LOTS_ON_PAGE = 20

FILE_NAME = 'data.csv'
FILE_KWARGS = {
    'sep': ';',
}


def get_num_pages_and_links(row: pd.Series, driver: webdriver) -> pd.Series:
    url = get_url_by_name(row['split_name'])
    loaded_all, loaded, soup = get_soup_by_url(url, driver, elements={'results': RESULTS_ELEMENTS,
                                                                      'lots': LOT_ELEMENTS})
    if loaded['results']['loaded']:
        # num_pages = get_num_pages_bs(soup)
        num_results = get_num_results_bs(soup)
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE + 1
        row['chr_num_pages'] = num_pages
    if loaded['lots']['loaded']:
        row['chr_links'] = get_links_bs(soup)

    return row


def get_num_pages(row: pd.Series, driver: webdriver) -> pd.Series:
    url = get_url_by_name(row['split_name'])
    loaded_all, loaded, soup = get_soup_by_url(url, driver, elements={'results': RESULTS_ELEMENTS})
    if loaded['results']['loaded']:
        num_results = get_num_results_bs(soup)
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE + 1
        row['chr_num_pages'] = num_pages
        row['chr_page'] = [i for i in range(1, num_pages + 1)]

    return row


def run():
    driver = webdriver.Chrome()
    data = get_names()
    data = data.apply(lambda x: get_num_pages_and_links(x, driver) if x['chr_num_pages'] == -1 else x,
                      axis=1).reset_index(drop=True)

    data = data.explode('chr_links')

    data.to_csv('students_data.csv')
    driver.close()


def not_for_students_(autosave: int = 100):
    driver = webdriver.Chrome()
    data = get_data(FILE_NAME, FILE_KWARGS)
    data = data.apply(lambda x: get_num_pages(x, driver) if x['chr_num_pages'] == -1 else x,
                      axis=1).reset_index(drop=True)

    data = data.explode('chr_page')
    for n, (i, row) in enumerate(data.iterrows()):
        if row['chr_links'] == ['No'] and not np.isnan(row['chr_page']):
            url = get_url_by_name(row['split_name'], page=int(row['chr_page']))
            logger.debug(f'Collecting lots for url: {url}')
            loaded_all, loaded, soup = get_soup_by_url(url, driver, elements={'lots': LOT_ELEMENTS})
            if loaded_all:
                row['chr_links'].remove('No')
                row['chr_links'].extend(get_links_bs(soup))

        if (n + 1) % autosave == 0:
            logger.warning('Writing data')
            data.to_csv(f'{FILE_NAME}', **FILE_KWARGS)
    logger.warning('Writing data')
    data.to_csv(f'{FILE_NAME}', **FILE_KWARGS)

    data = data.explode(column=['chr_links']).reset_index(drop=True)

    data.to_csv(FILE_NAME, **FILE_KWARGS)
    driver.close()


if __name__ == '__main__':
    # run()
    not_for_students_(autosave=100)
