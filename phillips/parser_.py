import time
from typing import List, Tuple, Dict, Any, Optional, Union
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger

PAGE_ELEMENTS = {
    'page_widget': (
        'div',
        {
            'class': 'pager'
        }
    ),
    'page_list': (
        'span',
        {
            'class': 'num'
        }
    ),
    'page_button': (
        'a',
        {}
    ),
}

LOT_ELEMENTS = {
    'lot_box_container': (
        'ul',
        {
            'class': 'standard-grid row search-results',
            'id': 'main-list-backbone'
        }
    ),
    'lot_box': (
        'li',
        {
            'class': 'col-xs-6 col-sm-3 search-result-item'
        }
    ),
    'lot_link': (
        'a',
        {
            'class': 'image-link'
        }
    )
}

RESULTS_ELEMENTS = {
    'results': (
        'h1',
        {
            'class': 'item-count-display'
        }
    ),
}


def load_check(soup: BeautifulSoup, elements: Optional[Dict[str, Dict[str, Tuple[str, Dict[str, str]]]]] = None)\
        -> Tuple[Dict[str, Dict[str, Union[bool, Dict[str, bool]]]], bool]:
    # logger.debug('Checking load')
    if elements is None:
        elements = {
            'page': PAGE_ELEMENTS,
            'lot': LOT_ELEMENTS,
            'results': RESULTS_ELEMENTS,
        }
    loaded = {}
    loaded_all = True
    for key, element in elements.items():
        # logger.debug(key)
        # logger.debug(element)
        loaded_ = {}
        loaded_all_ = True
        for key_, element_ in element.items():
            is_loaded = soup.find(*element_) is not None
            loaded_[key_] = is_loaded
            loaded_all = loaded_all and is_loaded
            loaded_all_ = loaded_all_ and is_loaded
        loaded[key] = {
            'loaded': loaded_all_,
            'details': loaded_
        }

    # logger.debug(loaded)
    return loaded, loaded_all


def get_soup_by_url(
        url: str,
        driver: webdriver,
        max_time: float = 2,
        elements: Optional[Dict[str, Dict[str, Tuple[str, Dict[str, str]]]]] = None
) -> Tuple[bool, Dict[str, Dict[str, Union[bool, Dict[str, bool]]]], BeautifulSoup]:
    logger.info(f'Processing url: {url}')
    driver.get(url)
    start_time = datetime.now()
    loaded_all = False
    loaded = {}
    soup = None
    while not loaded_all and (datetime.now() - start_time).total_seconds() < max_time:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        loaded, loaded_all = load_check(soup, elements)
    if loaded_all:
        logger.success(f'Successfully loaded page')
    else:
        logger.warning(f'Page not fully loaded')
        for key, l in loaded.items():
            if l['loaded']:
                logger.success(f'\t{key} is fully loaded')
            else:
                for k, l_ in l['details'].items():
                    if l_:
                        logger.success(f'\t\t{k} was found')
                    else:
                        logger.error(f'\t\t{k} was not found')


    return loaded_all, loaded, soup


def get_num_pages_bs(soup: BeautifulSoup) -> int:
    pages_num_widget = soup.find(*PAGE_ELEMENTS['page_widget'])
    if pages_num_widget is not None:
        page_list = pages_num_widget.find(*PAGE_ELEMENTS['page_list'])
        page_link = page_list.find_all(*PAGE_ELEMENTS['page_button'])[-1]['href']
        page_num = int(page_link.split('/')[2])
    else:
        page_num = 1

    return page_num


def get_num_results_bs(soup: BeautifulSoup) -> int:
    results_text = soup.find(*RESULTS_ELEMENTS['results']).text

    results = results_text.split()[-2]
    logger.info(f'Found {results} results')

    return int(results)


def get_links_bs(soup: BeautifulSoup) -> List[str]:
    soup = soup.find(*LOT_ELEMENTS['lot_box_container'])
    lots = soup.find_all(*LOT_ELEMENTS['lot_box'])
    logger.info(f'Collecting links to lots')

    links = [lot.find(*LOT_ELEMENTS['lot_link'])['href'] for lot in lots]
    if links:
        logger.success(f'Collected {str(len(links))} links')
    else:
        logger.warning(f'No links were found')

    return links


def get_url_by_name(name: str, page: int = 1) -> str:
    return f'https://www.phillips.com/search/{str(page)}?search={name.replace(" ", "+")}'


if __name__ == '__main__':
    driver = webdriver.Chrome()
    url = get_url_by_name('Edward Steichen')
    print(url)
    loaded_all, loaded, soup = get_soup_by_url(url, driver)

    results = get_num_results_bs(soup)
