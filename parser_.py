import time
from typing import List, Tuple, Dict, Any, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
import json


class Parser:
    def __init__(self):
        caps = DesiredCapabilities().CHROME
        caps['pageLoadStrategy'] = 'eager'
        self.driver = webdriver.Chrome(desired_capabilities=caps)
        logger.info('Loading elements')
        with open('elements.json', 'r') as f:
            self.elements = json.load(f)
            logger.success('Done')
        self.auction = None
        self.soup = None

    def set_auction(self, auction):
        assert auction in self.elements.keys()
        self.auction = auction

    def get_soup(self):
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def soup_check(self, elements: Optional[List[str]] = None)\
            -> Tuple[Dict[str, Dict[str, Union[bool, Dict[str, bool]]]], bool]:
        if elements is None:
            elements = self.elements[self.auction].keys()
        else:
            assert set(elements).issubset(set(self.elements[self.auction].keys()))
            elements = {key: self.elements[self.auction][key] for key in elements}

        loaded = {}
        loaded_all = True
        for key, element in elements.items():
            # logger.debug(key)
            # logger.debug(element)
            loaded_ = {}
            loaded_all_ = True
            for key_, element_ in element.items():
                is_loaded = self.soup.find(*element_) is not None
                loaded_[key_] = is_loaded
                loaded_all = loaded_all and is_loaded
                loaded_all_ = loaded_all_ and is_loaded
            loaded[key] = {
                'loaded': loaded_all_,
                'details': loaded_
            }

        # logger.debug(loaded)
        return loaded, loaded_all

    def load_page(self, url: str, max_time: float = 2, elements: Optional[List[str]] = None)\
            -> Tuple[bool, Dict[str, Dict[str, Union[bool, Dict[str, bool]]]]]:
        logger.info(f'Processing url: {url}')
        self.driver.get(url)
        start_time = datetime.now()
        loaded_all = False
        loaded = {}
        soup = None
        while not loaded_all and (datetime.now() - start_time).total_seconds() < max_time:
            self.get_soup()
            loaded, loaded_all = self.soup_check(elements)
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

        return loaded_all, loaded

    def get_num_pages(self) -> int:
        elements = self.elements[self.auction]['page_elements']
        if self.auction == 'christies':
            pages_num_widget = self.soup.find(*elements['page_list'])
            if pages_num_widget is not None:
                buttons = pages_num_widget.find_all(*elements['page_button'])
                page_num = int(buttons[-1].find(*elements['page_text']).text)
            else:
                page_num = 1

            return page_num
        elif self.auction == 'phillips':
            pages_num_widget = self.soup.find(*elements['page_widget'])
            if pages_num_widget is not None:
                page_list = pages_num_widget.find(*elements['page_list'])
                page_link = page_list.find_all(*elements['page_button'])[-1]['href']
                page_num = int(page_link.split('/')[2])
            else:
                page_num = 1

            return page_num
        else:
            logger.error(f'Unknown auction ({self.auction})')
            return -1

    def get_num_results(self) -> int:
        elements = self.elements[self.auction]['results_elements']
        if self.auction == 'christies':
            carousel = self.soup.find(*elements['results_carousel'])
            button = carousel.find(*elements['results_button'])
            results_text = button.find_all(*elements['results_num'])[-1].text

            results = ''.join(results_text[1:-1].split('+')[0].split(','))
            logger.info(f'Found {results_text}={results} results')

            return int(results)
        elif self.auction == 'phillips':
            results_text = self.soup.find(*elements['results']).text

            results = results_text.split()[-2]
            logger.info(f'Found {results} results')

            return int(results)
        else:
            logger.error(f'Unknown auction ({self.auction})')
            return -1

    def get_links(self) -> List[str]:
        elements = self.elements[self.auction]['lot_elements']
        soup = self.soup.find(*elements['lot_box_container'])
        lots = soup.find_all(*elements['lot_box'])
        if self.auction == 'phillips':
            lots += soup.find_all(*elements['lot_box_pending'])
        logger.info(f'Collecting links to lots')

        links = [lot.find(*elements['lot_link'])['href'] for lot in lots]
        if links:
            logger.success(f'Collected {str(len(links))} links')
        else:
            logger.warning(f'No links were found')

        return links

    def get_url_by_name(self, name: str, page: int = 1) -> str:
        if self.auction == 'christies':
            return f'https://www.christies.com/search?' \
                   f'entry={name.replace(" ", "%20")}&page={str(page)}&sortby=relevance&tab=sold_lots'
        elif self.auction == 'phillips':
            return f'https://www.phillips.com/search/{str(page)}?search={name.replace(" ", "+")}'
        else:
            logger.error(f'Unknown auction ({self.auction})')
            return ''
