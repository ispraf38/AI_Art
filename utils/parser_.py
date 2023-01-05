import time
from typing import List, Tuple, Dict, Any, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
import json


class Parser:
    def __init__(self, elements_path: Optional[str] = None):
        self.driver = None
        self.set_driver()
        logger.info('Loading elements')
        if elements_path is None:
            elements_path = '../elements.json'
        with open(elements_path, 'r') as f:
            self.ELEMENTS = json.load(f)
            logger.success('Done')
        self.elements = {}
        self.auction = None
        self.soup = None

    def set_driver(self):
        self.driver = webdriver.Chrome()

    def set_auction(self, auction):
        assert auction in self.ELEMENTS.keys()
        self.auction = auction
        self.elements = self.ELEMENTS[auction]

    def get_soup(self):
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def soup_check(self, elements: Optional[List[str]] = None) -> Any:
        if elements is None:
            elements = {}
        else:
            assert set(elements).issubset(set(self.elements.keys()))
            elements = {key: self.elements[key] for key in elements}

        loaded = {}
        loaded_all = True
        for key, element in elements.items():
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
        return loaded, loaded_all

    def load_page(self, url: str, max_time: float = 5, elements: Optional[List[str]] = None) -> Any:
        logger.info(f'Processing url: {url}')
        self.driver.get(url)
        start_time = datetime.now()
        loaded_all = False
        loaded = {}
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


class ChristiesParser(Parser):
    def __init__(self, *args, **kwargs):
        super(ChristiesParser, self).__init__(*args, **kwargs)
        self.set_auction('christies')

    def get_url_by_name(self, name: str, page: int = 1) -> str:
        return f'https://www.christies.com/search?' \
               f'entry={name.replace(" ", "%20")}&page={str(page)}&sortby=relevance&tab=sold_lots'

    def get_num_pages(self) -> int:
        elements = self.elements['page_elements']
        pages_num_widget = self.soup.find(*elements['page_list'])
        if pages_num_widget is not None:
            buttons = pages_num_widget.find_all(*elements['page_button'])
            page_num = int(buttons[-1].find(*elements['page_text']).text)
        else:
            page_num = 1

        return page_num

    def get_num_results(self) -> int:
        elements = self.elements['results_elements']
        carousel = self.soup.find(*elements['results_carousel'])
        button = carousel.find(*elements['results_button'])
        results_text = button.find_all(*elements['results_num'])[-1].text

        results = ''.join(results_text[1:-1].split('+')[0].split(','))
        logger.info(f'Found {results_text}={results} results')

        return int(results)

    def get_links(self) -> List[str]:
        elements = self.elements['lot_elements']
        soup = self.soup.find(*elements['lot_box_container'])
        lots = soup.find_all(*elements['lot_box'])
        logger.info(f'Collecting links to lots')

        links = [lot.find(*elements['lot_link'])['href'] for lot in lots]
        if links:
            logger.success(f'Collected {str(len(links))} links')
        else:
            logger.warning(f'No links were found')

        return links


class PhillipsParser(Parser):
    def __init__(self, *args, **kwargs):
        super(PhillipsParser, self).__init__(*args, **kwargs)
        self.set_auction('phillips')

    def set_driver(self):
        caps = DesiredCapabilities().CHROME
        caps['pageLoadStrategy'] = 'eager'
        self.driver = webdriver.Chrome(desired_capabilities=caps)

    def get_url_by_name(self, name: str, page: int = 1) -> str:
        return f'https://www.phillips.com/search/{str(page)}?search={name.replace(" ", "+")}'

    def get_num_pages(self) -> int:
        elements = self.elements['page_elements']
        pages_num_widget = self.soup.find(*elements['page_widget'])
        if pages_num_widget is not None:
            page_list = pages_num_widget.find(*elements['page_list'])
            page_link = page_list.find_all(*elements['page_button'])[-1]['href']
            page_num = int(page_link.split('/')[2])
        else:
            page_num = 1

        return page_num

    def get_num_results(self) -> int:
        elements = self.elements['results_elements']
        results_text = self.soup.find(*elements['results']).text

        results = results_text.split()[-2]
        logger.info(f'Found {results} results')

        return int(results)

    def get_links(self) -> List[str]:
        elements = self.elements['lot_elements']
        soup = self.soup.find(*elements['lot_box_container'])
        lots = soup.find_all(*elements['lot_box'])
        lots += soup.find_all(*elements['lot_box_pending'])
        logger.info(f'Collecting links to lots')

        links = [lot.find(*elements['lot_link'])['href'] for lot in lots]
        if links:
            logger.success(f'Collected {str(len(links))} links')
        else:
            logger.warning(f'No links were found')

        return links


class AutoParser(Parser):
    def __init__(self, auction: str, elements_path: str = '../elements_auto.json'):
        super(AutoParser, self).__init__(elements_path=elements_path)
        self.set_auction(auction)

    def set_driver(self):
        caps = DesiredCapabilities().CHROME
        caps['pageLoadStrategy'] = 'eager'
        self.driver = webdriver.Chrome(desired_capabilities=caps)

    def log_details(self, details: Dict[str, Any], level: int = 0):
        for key, value in details.items():
            if value['loaded_all']:
                logger.success('\t' * level + f'{key} is fully loaded')
            else:
                if value['loaded']:
                    logger.warning('\t' * level + f'{key} is not fully loaded')
                    self.log_details(value['details'], level + 1)
                else:
                    logger.error('\t' * level + f'{key} is not loaded')

    def element_check(self, soup, element):
        soup_ = soup.find(*element['attrs'])
        loaded = soup_ is not None
        loaded_all = loaded
        details = {}
        if loaded and 'children' in element:
            for element_name, element_ in element['children'].items():
                loaded_, loaded_all_, details_ = self.element_check(soup_, element_)
                details[element_name] = {
                    'loaded': loaded_,
                    'loaded_all': loaded_all_,
                    'details': details_,
                }
                loaded_all = loaded_all and loaded_all_

        return loaded, loaded_all, details

    def soup_check(self, elements: Optional[List[str]] = None) -> Any:
        if elements is None:
            elements = {}
        else:
            assert set(elements).issubset(set(self.elements.keys()))
            elements = {key: self.elements[key] for key in elements}

        details = {}
        loaded_all = True

        for key, element in elements.items():
            loaded, loaded_all_, details_ = self.element_check(self.soup, element)
            loaded_all = loaded_all and loaded_all_
            details[key] = {
                'loaded': loaded,
                'loaded_all': loaded_all_,
                'details': details_,
            }

        return loaded_all, details

    def load_page(self, url: str, max_time: float = 5, elements: Optional[List[str]] = None) -> Any:
        logger.info(f'Processing url: {url}')
        self.driver.get(url)
        start_time = datetime.now()
        loaded_all = False
        details = {}
        while not loaded_all and (datetime.now() - start_time).total_seconds() < max_time:
            self.get_soup()
            loaded_all, details = self.soup_check(elements)

        with open('test.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        if loaded_all:
            logger.success('Successfully loaded page')
        else:
            self.log_details(details)

        return loaded_all, details

    def parse_element_(self, name: str, element: Dict[str, Any], soups: List[BeautifulSoup])\
            -> Dict[str, Any]:
        results = {}
        soups_ = []
        for soup in soups:
            if 'find_all' in element and element['find_all']:
                if 'element_num' not in element or element['element_num'] is None:
                    soups_.extend(soup.find_all(*element['attrs']))
                else:
                    soups_.append(soup.find_all(*element['attrs'])[element['element_num']])
            else:
                soups_.append(soup.find(*element['attrs']))
        if 'children' in element and element['children']:
            for name_, element_ in element['children'].items():
                results.update(self.parse_element_(name_, element_, soups_))
        if 'desired_attr' in element and element['desired_attr'] is not None:
            if element['desired_attr'] == 'text':
                results[name] = [soup.text for soup in soups_]
            else:
                results[name] = [soup[element['desired_attr']] for soup in soups_]

        return results

    def parse_element(self, name: str) -> Dict[str, Any]:
        return self.parse_element_(name, self.elements[name], [self.soup])
