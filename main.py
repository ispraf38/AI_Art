import pandas as pd
import numpy as np
from loguru import logger
from data_handler import get_names, get_data
from parser_ import get_url_by_name, get_soup_by_url, get_num_pages_bs, get_num_results_bs, get_links_bs
from parser_ import PAGE_ELEMENTS, LOT_ELEMENTS, RESULTS_ELEMENTS
from selenium import webdriver

MAX_LOTS_ON_PAGE = 20

FILE_NAME = 'data.csv'
FILE_KWARGS = {
    'sep': ';'
}


def get_num_pages(row: pd.Series, driver: webdriver) -> pd.Series:
    url = get_url_by_name(row['name'])
    loaded_all, loaded, soup = get_soup_by_url(url, driver, elements={'results': RESULTS_ELEMENTS, 'lots': LOT_ELEMENTS})
    if loaded['results']['loaded']:
        # num_pages = get_num_pages_bs(soup)
        num_results = get_num_results_bs(soup)
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE + 1
        row['chr_num_pages'] = num_pages
        row['chr_page'] = [i for i in range(1, num_pages + 1)]
    if loaded['lots']['loaded']:
        row['chr_links'] = get_links_bs(soup)
    if loaded_all:
        row['handled'] = True

    return row


def get_lot_links(row: pd.Series, driver: webdriver) -> pd.Series:
    url = get_url_by_name(row['name'])
    loaded_all, loaded, soup = get_soup_by_url(url, driver, elements={'lots': LOT_ELEMENTS})
    if loaded['lots']['loaded']:
        row['chr_links'] = get_links_bs(soup)

    return row


if __name__ == '__main__':
    driver = webdriver.Chrome()
    data = get_data()
    data.to_csv('test1.csv', sep=';')

    if (data['chr_num_pages'] == -1).any():
        data = data.apply(lambda x: get_num_pages(x, driver) if x['chr_num_pages'] == -1 else x,
                          axis=1).reset_index(drop=True)
        # data = data.explode(column=['chr_page']).reset_index(drop=True)
    data.to_csv(FILE_NAME, **FILE_KWARGS)

    data = data.explode(column=['chr_links']).reset_index(drop=True)

    data.to_csv('data1.csv', **FILE_KWARGS)
