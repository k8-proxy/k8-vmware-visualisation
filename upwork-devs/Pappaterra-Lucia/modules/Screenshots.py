#coding=utf-8
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URLS = ['http://0.0.0.0:8080/html%20pages/VMs-0.html',
        'http://0.0.0.0:8080/html%20pages/VMs-1.html',
        'http://0.0.0.0:8080/html%20pages/VMs-2.html',
        'http://0.0.0.0:8080/html%20pages/VMs-3.html',
        'http://0.0.0.0:8080/html%20pages/VMs-4.html',
        'http://0.0.0.0:8080/html%20pages/Release.html']


def take_screenshot(URL):

    NAME = (URL.split('html%20pages/'))[1].split('.html')[0]

    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    driver.get(URL)

    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment
    time.sleep(2)
    driver.find_element_by_tag_name('body').screenshot('data/screenshot_'+NAME+'.png')

    driver.quit()

    print(NAME + '.html screenshot done')


for URL in URLS:
    take_screenshot(URL)
