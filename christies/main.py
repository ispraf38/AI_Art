import pandas as pd
from loguru import logger
from data_handler import get_data
from christies.parser_ import get_url_by_name, get_soup_by_url, get_num_results_bs, get_links_bs
from christies.parser_ import LOT_ELEMENTS, RESULTS_ELEMENTS
from selenium import webdriver

MAX_LOTS_ON_PAGE = 20

FILE_NAME = 'data.csv'
FILE_KWARGS = {
    'sep': ';',
}


def get_num_pages(row: pd.Series, driver: webdriver) -> pd.Series:
    url = get_url_by_name(row['split_name'])
    loaded_all, loaded, soup = get_soup_by_url(url, driver, elements={'results': RESULTS_ELEMENTS, 'lots': LOT_ELEMENTS})
    if loaded['results']['loaded']:
        # num_pages = get_num_pages_bs(soup)
        num_results = get_num_results_bs(soup)
        num_pages = (num_results - 1) // MAX_LOTS_ON_PAGE + 1
        row['chr_num_pages'] = num_pages
        row['chr_page'] = [i for i in range(1, num_pages + 1)]
    if loaded['lots']['loaded']:
        row['chr_links'] = get_links_bs(soup)

    return row


def not_for_students(row: pd.Series, driver: webdriver) -> pd.Series:
    if row['chr_page'] <= 1:
        return row

    url = get_url_by_name(row['split_name'], page=row['chr_page'])
    logger.debug(f'Collecting lots for url: {url}')
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

    students_data = data.explode(column=['chr_links'])

    students_data.to_csv(f'students_{FILE_NAME}', **FILE_KWARGS)

    logger.success('Students dataset created')
    data.to_csv('test2.csv', sep=';')

    data = data.explode(column=['chr_page'])
    data.to_csv('test3.csv', sep=';')

    data = data.apply(lambda x: not_for_students(x, driver), axis=1)

    data = data.explode(column=['chr_links']).reset_index(drop=True)

    data.to_csv(f'final_{FILE_NAME}', **FILE_KWARGS)

    driver.close()

