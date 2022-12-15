from data_handler import get_names
from parser_ import get_links_by_name
from selenium import webdriver

driver = webdriver.Chrome()
names = get_names()
links = []
for name in names:
    links.extend(get_links_by_name(name, driver))

print(links)