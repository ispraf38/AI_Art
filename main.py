import pandas as pd
import numpy as np
from loguru import logger
from data_handler import get_names, get_data
from parser_ import get_links_by_name, get_url_by_name, get_soup_by_url, get_num_pages_bs
from parser_ import PAGE_ELEMENTS
from selenium import webdriver


FILE_NAME = 'data.csv'
FILE_KWARGS = {
    'sep': ';'
}


def get_num_pages(row: pd.Series, driver: webdriver) -> pd.Series:
    url = get_url_by_name(row['name'])
    loaded, soup = get_soup_by_url(url, driver, elements=PAGE_ELEMENTS)
    if loaded:
        num_pages = get_num_pages_bs(soup)
        row['chr_num_pages'] = num_pages
        row['page'] = np.arange(1, num_pages + 1)
    else:
        logger.debug(f'Page {url} loaded with errors. Skipping')

    return row


if __name__ == '__main__':
    driver = webdriver.Chrome()
    data = get_data()
    data.to_csv('test1.csv', sep=';')

    if (data['chr_num_pages'] == -1).any():
        data = data.apply(lambda x: get_num_pages(x, driver), axis=1)
        data = data.explode(column=['page'])

    data.to_csv(FILE_NAME, **FILE_KWARGS)
