import time
from typing import List, Tuple, Dict, Any, Optional, Union
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger

PAGE_ELEMENTS = {
    'page_list': (
        'ul',
        {
            'class': 'chr-page-pagination__list'
        }
    ),
    'page_button': (
        'li',
        {}
    ),
    'page_text': (
        'span',
        {
            'class': 'chr-button__text'
        }
    ),
}

LOT_ELEMENTS = {
    'lot_box_container': (
        'div',
        {
            'class': 'chr-search-lots-view__column-transition col-12 col-lm-8 col-lg-9 col-xl-9'
        }
    ),
    'lot_box': (
        'div',
        {
            'class': 'chr-search-lots-view__column-transition chr-search-lots-view__tile-section col-sm-6 col-md-4 '
                     'chr-search-results tile-gutter col-lm-6 col-lg-4 col-xl-4'
        }
    ),
    'lot_link': (
        'a',
        {
            'class': 'chr-lot-tile__link'
        }
    )
}

RESULTS_ELEMENTS = {
    'results_carousel': (
        'div',
        {
            'class': 'chr-scrolling-carousel__content'
        }
    ),
    'results_button': (
        'button',
        {
            'title': 'Sold Lots'
        }
    ),
    'results_num': (
        'span',
        {}
    )
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
    pages_num_widget = soup.find(*PAGE_ELEMENTS['page_list'])
    if pages_num_widget is not None:
        buttons = pages_num_widget.find_all('li')
        page_num = int(buttons[-1].find(*PAGE_ELEMENTS['page_text']).text)
    else:
        page_num = 1

    return page_num


def get_num_results_bs(soup: BeautifulSoup) -> int:
    carousel = soup.find(*RESULTS_ELEMENTS['results_carousel'])
    button = carousel.find(*RESULTS_ELEMENTS['results_button'])
    results_text = button.find_all(*RESULTS_ELEMENTS['results_num'])[-1].text

    results = ''.join(results_text[1:-1].split('+')[0].split(','))
    logger.info(f'Found {results_text}={results} results')

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
    return f'https://www.christies.com/search?' \
           f'entry={name.replace(" ", "%20")}&page={str(page)}&sortby=relevance&tab=sold_lots'


def get_links_by_name(name: str, driver: webdriver) -> List[str]:
    logger.info(f'Collecting links by name: {name}')

    url = get_url_by_name(name)

    loaded, soup = get_soup_by_url(url, driver)
    links = []
    if loaded:
        page_num = get_num_pages_bs(soup)
        links = get_links_bs(soup)
        for p in range(2, page_num + 1):
            url = get_url_by_name(name, p)
            loaded, soup = get_soup_by_url(url, driver)
            if loaded:
                links.extend(get_links_bs(soup))
    else:
        logger.debug(f'Page loaded with errors. Skipping')
    return links


if __name__ == '__main__':
    driver = webdriver.Chrome()
    links = get_links_by_name('Edward Steichen', driver)
    print(links)
