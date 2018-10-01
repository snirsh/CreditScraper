########################################################################################################################
####                                           IMPORTS                                                              ####
########################################################################################################################
import sys
from urllib.request import urlopen
from urllib import error
from bs4 import BeautifulSoup
import unicodecsv as csv
from urllib.request import build_opener
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests

########################################################################################################################
####                                             URLS                                                               ####
########################################################################################################################
URL_ISRACARD_HOME = 'https://www1.isracard.co.il/home'
URL_ISRACARD_MOREGIFTS = 'https://www1.isracard.co.il/moregits'
URL_ISRACARD_ATTRACTIONS = 'https://www1.isracard.co.il/attractions'
URL_ISRACARD_FASHION = 'https://www1.isracard.co.il/2fashion'
URL_ISRACARD_COOK = 'https://www1.isracard.co.il/cook'
URL_ISRACARD_PARENTS = 'https://www1.isracard.co.il/parents'
URL_ISRACARD_LOCAL = 'https://www1.isracard.co.il/start/Pages1/IsraLocal/'
URLS_ISRACARD = [URL_ISRACARD_ATTRACTIONS, URL_ISRACARD_COOK, URL_ISRACARD_FASHION, URL_ISRACARD_HOME,
                 URL_ISRACARD_MOREGIFTS, URL_ISRACARD_PARENTS, URL_ISRACARD_LOCAL]
URL_LEUMI = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/BenfitsGallery.aspx'
URL_CAL = 'https://cashback-plus.co.il/stores/all-stores/'
########################################################################################################################
####                                        COMPANY NAMES                                                           ####
########################################################################################################################
ISRACARD_STR = 'Isracard'
LEUMI_STR = 'Leumi Card'
CAL_STR = 'CalCashBack'
########################################################################################################################
####                                           CONSTANTS                                                            ####
########################################################################################################################
HTML_PARSER = 'html.parser'
DIV = 'div'
CLASS = 'class'
STYLE = 'style'
HREF = 'href'
SPAN = 'span'
A_STR = 'a'
P_STR = 'p'
H1 = 'h1'
H3 = 'h3'
H4 = 'h4'
H5 = 'h5'
TD = 'td'
JOB_STR = 'job'
TITLE_STR = 'title'
LEUMI_HOST = 'https://www.leumi-card.co.il/'
LEUMI_ORIGIN = 'https://www.leumi-card.co.il/'
LEUMI_REFERER = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/BenfitsGallery.aspx'
"""
Main scraper:
this function runs all the scrapers at once and generates a CSV file
"""


def scraper():
    companies = [ISRACARD_STR, LEUMI_STR, CAL_STR]
    with open('benefits.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        benefits = {}
        for company in companies:
            scrape_by_name(company, benefits)
        for key, value in benefits.items():
            try:
                writer.writerow([str(key[0]), str(key[1]), str(value)])
            except csv.Error:
                print('CSV writing error', sys.exc_info()[0])
                raise
        csvfile.close()


"""
this function scrapes by name
"""


def scrape_by_name(name, benefits):
    if name == ISRACARD_STR:
        return isracard_scraper(benefits)
    if name == LEUMI_STR:
        return leumi_scraper(benefits)
    if name == CAL_STR:
        return cal_scraper(benefits)

def scraping_unit(page_url):
    try:
        page = urlopen(page_url)
        soup = BeautifulSoup(page, HTML_PARSER)
    except error.HTTPError:
        headers = [('User-Agent', 'Mozilla/5.0')]
        opener = build_opener()
        opener.addheaders = headers
        page = opener.open(page_url)
        soup = BeautifulSoup(page, HTML_PARSER)
    return soup


def requests_unit(page_url, host, origin, referer, data):
    session = requests.Session()
    session.get(url=page_url, allow_redirects=True)
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Host": host,
        "Origin": origin,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Referer": referer,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,he;q=0.8,fr;q=0.7",
        "X-MicrosoftAjax": "Delta=true",
        "X-Requested-With": "XMLHttpRequest"}
    response = session.post(url=url, data=data, headers=headers, allow_redirects=True)
    print(response.text)


def isracard_scraper(benefits):
    for URL in URLS_ISRACARD:
        soup = scraping_unit(URL)
        for benefit in soup.findAll(DIV, attrs={CLASS: 'benefotTab-info'}):
            title = benefit.findNext(H3, attrs={CLASS: 'f14'})
            desc = benefit.findNext(P_STR, attrs={CLASS: 'f13'})
            benefits[(ISRACARD_STR, title.text.strip())] = desc.text.strip()


def leumi_scraper(benefits):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome("C:/Users/Snir/Downloads/chromedriver_win32/chromedriver.exe", options=chrome_options)
    driver.set_window_size(1000, 800)
    driver.get(URL_LEUMI)
    try:
        while True:
            soup = BeautifulSoup(driver.page_source, HTML_PARSER)
            for benefit in soup.findAll(DIV, attrs={CLASS: 'linkWapper'}):
                title = benefit.findNext(SPAN)
                desc = benefit.findNext(P_STR)
                benefits[(LEUMI_STR, title.text.strip())] = desc.text.strip()
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="divPager"]/ul/li[12]')))
            next_page = driver.find_element_by_xpath('//*[@id="divPager"]/ul/li[12]')
            next_page.click()
    except NoSuchElementException:
        return
    except TimeoutException:
        return


def cal_scraper(benefits):
    soup = scraping_unit(URL_CAL)
    for benefit in soup.findAll(SPAN, attrs={CLASS: 'sr-only'}):
        title = benefit
        desc = benefit.findNext(H1, attrs={CLASS: 'h4 bold'})
        benefits[(CAL_STR, title.text.strip())] = desc.text.strip()


if __name__ == '__main__':
    scraper()
