########################################################################################################################
####                                           IMPORTS                                                              ####
########################################################################################################################
import sys
import time
from urllib.request import urlopen
from urllib import error

from airtable import Airtable
from bs4 import BeautifulSoup
import unicodecsv as csv
from urllib.request import build_opener
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, ElementNotVisibleException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests
from selenium.webdriver.support.select import Select

########################################################################################################################
####                                             URLS                                                               ####
########################################################################################################################
from urllib3.util import wait

URL_ISRACARD_HOME = 'https://www1.isracard.co.il/home'
URL_ISRACARD_MOREGIFTS = 'https://www1.isracard.co.il/moregits'
URL_ISRACARD_ATTRACTIONS = 'https://www1.isracard.co.il/attractions'
URL_ISRACARD_FASHION = 'https://www1.isracard.co.il/2fashion'
URL_ISRACARD_COOK = 'https://www1.isracard.co.il/cook'
URL_ISRACARD_PARENTS = 'https://www1.isracard.co.il/parents'
URL_ISRACARD_TRAVELS = 'https://www1.isracard.co.il/travels'
URL_ISRACARD_ART = 'https://www1.isracard.co.il/art'
URLS_ISRACARD = {'אטרקציות': URL_ISRACARD_ATTRACTIONS, 'עיצוב ומוצרים לבית': URL_ISRACARD_HOME,
                 'עוד הפתעות': URL_ISRACARD_MOREGIFTS, 'אופנה': URL_ISRACARD_FASHION, 'אוכל': URL_ISRACARD_COOK,
                 'הורים וילדים': URL_ISRACARD_PARENTS, 'טיולים': URL_ISRACARD_TRAVELS, 'תרבות': URL_ISRACARD_ART}

URL_LEUMI_MOVIES = 'https://www.leumi-card.co.il/he-il/Benefits/BenefitsPlus/Movies/Pages/MoviesGallery.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_ENTERTAINMENT = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/Entertainment.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_ATTRACTIONS = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/atractions.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_RESTAURATNS = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/rest.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_LEISURE = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/Leisure.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_KIDS = 'https://www.leumi-card.co.il/he-il/Benefits/Pages/Kids.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_DAILY = 'https://www.leumi-card.co.il/he-il/Benefits/DailyBenefits/Pages/DailyBenefitsGallery.aspx?sourceGA=AllBenefitsBox'
URL_LEUMI_DISCOUNTS = 'https://www.leumi-card.co.il/he-il/Benefits/LeumiCard/discounts/Pages/DisPlus.aspx?sourceGA=AllBenefitsBox'
URLS_LEUMI = {'סרטים': URL_LEUMI_MOVIES, 'מופעים והצגות': URL_LEUMI_ENTERTAINMENT,
              'אטרקציות': URL_LEUMI_ATTRACTIONS, 'מסעדות': URL_LEUMI_RESTAURATNS, 'נופש ופנאי': URL_LEUMI_LEISURE,
              'ילדים': URL_LEUMI_KIDS,
              'פינוק היום': URL_LEUMI_DAILY, 'הנחות': URL_LEUMI_DISCOUNTS}
URL_PAYBACK = 'https://www.pay-back.co.il/category/all'

URL_CAL_CASHBACK = 'https://cashback-plus.co.il/stores/all-stores/'
URL_AMERICANEXPRESS = 'https://rewards.americanexpress.co.il/'
URL_CAL = 'https://www.callatet.co.il/BuildaGate5/general2/company_search_tree.php?NewNameMade=5868&SiteName=takti'
########################################################################################################################
####                                        COMPANY NAMES                                                           ####
########################################################################################################################
ISRACARD_STR = 'Isracard'
LEUMI_STR = 'Leumi Card'
LEUMI_PAYBACK_STR = 'Leumi Payback'
CAL_CASHBACK_STR = 'CalCashBack'
AMERICANEXPRESS_STR = 'American Express'
CAL_STR = 'Cal'
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
    # companies = [ISRACARD_STR, LEUMI_STR, CAL_CASHBACK_STR, AMERICANEXPRESS_STR]
    companies = [ISRACARD_STR]
    print('Started scraping:\n')
    benefits = {}
    for company in companies:
        print('Started scraping ' + company + '.\n')
        scrape_by_name(company, benefits)
    print('Finished the current scrape, current number of benefits: ' + str(len(benefits)) + '\n')
    question = input("Press 0 for CSV and 1 for Airtable \t")
    if question == str(0):
        with open('benefits.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            print('Finished scraping, now Starting to write to CSV a total of ' + str(len(benefits)) + '.')
            for key, value in benefits.items():
                try:
                    writer.writerow([str(key[0]), str(key[1]), str(value)])
                except csv.Error:
                    print('CSV writing error', sys.exc_info()[0])
                    raise
            csvfile.close()
    elif question == str(1):
        print("Updating airtable")
        airtable = Airtable('app4iqBeamg7ClHPS', 'Benefits', api_key='keyaVQTgUd3hczqsE')
        benefit_str = 'Benefit'
        company_str = 'Company'
        description_str = 'Benefit description'
        for key, value in benefits.items():
            airtable.insert({benefit_str: key[1], company_str: key[0], description_str: value})


"""
this function scrapes by name
"""


def scrape_by_name(name, benefits):
    if name == ISRACARD_STR:
        return isracard_scraper(benefits)
    if name == LEUMI_STR:
        return leumi_scraper(benefits)
    if name == CAL_CASHBACK_STR:
        return cal_cashback_scraper(benefits)
    if name == AMERICANEXPRESS_STR:
        return americanexpress_scraper(benefits)
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


def webdriver_unit(debugging=False):
    chrome_options = webdriver.ChromeOptions()
    if not debugging:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def isracard_scraper(benefits):
    driver = webdriver_unit()
    i = 1
    url_num = 0
    for subject, URL in URLS_ISRACARD.items():
        url_num += 1
        print('Current URL: ' + str(url_num) + ' out of ' + str(len(URLS_ISRACARD)))
        if url_num == len(URLS_ISRACARD):
            print('\n')
        driver.get(URL)
        try:
            more_benefits = driver.find_element_by_xpath('//*[@id="showMoreHotBenefits"]')
            more_benefits.click()
        except NoSuchElementException:
            continue
        except TimeoutException:
            return
        except ElementNotVisibleException:
            continue
        finally:
            soup = BeautifulSoup(driver.page_source, HTML_PARSER)
            for benefit in soup.findAll(H1, attrs={CLASS: 'f14'}):
                title = benefit.text.strip()
                desc = benefit.findNext(P_STR, attrs={CLASS: 'f13'}).text.strip()
                benefits[(ISRACARD_STR + ": " + subject, str(i) + ". " + title)] = desc
                i += 1


def leumi_scraper(benefits):
    leumi_payback_scraper(benefits)  # Payback site
    i = 1
    driver = webdriver_unit()
    url_num = 0
    for subject, url in URLS_LEUMI.items():
        url_num += 1
        print('Current URL: ' + str(url_num) + ' out of ' + str(len(URLS_LEUMI)))
        if url_num == len(URLS_LEUMI):
            print('\n')
        driver.get(url)
        try:
            while True:
                next_page = driver.find_elements_by_xpath('//*[@id="divPager"]/ul/li')[-1]
                soup = BeautifulSoup(driver.page_source, HTML_PARSER)
                for benefit in soup.findAll(DIV, attrs={CLASS: 'linkWapper'}):
                    title = benefit.findNext(SPAN)
                    desc = benefit.findNext(P_STR)
                    benefits[(LEUMI_STR + ": " + subject, str(i) + ". " + title.text.strip())] = desc.text.strip()
                    i += 1
                if next_page.get_attribute(CLASS) != 'gcpPage left':
                    break
                next_page.click()
                time.sleep(1)
        except IndexError:
            soup = BeautifulSoup(driver.page_source, HTML_PARSER)
            for benefit in soup.findAll(DIV, attrs={CLASS: 'linkWapper'}):
                title = benefit.findNext(SPAN)
                desc = benefit.findNext(P_STR)
                benefits[(LEUMI_STR + ": " + subject, str(i) + ". " + title.text.strip())] = desc.text.strip()
                i += 1
        except TimeoutException:
            return


def leumi_payback_scraper(benefits):
    soup = scraping_unit(URL_PAYBACK)
    i = 1
    for benefit in soup.findAll(DIV, attrs={CLASS: 'slider'}):
        title = benefit.findNext(DIV).text
        desc = benefit.findNext(H4)
        benefits[(LEUMI_STR, str(i) + ". " + title)] = desc
        i += 1


def cal_cashback_scraper(benefits):
    soup = scraping_unit(URL_CAL_CASHBACK)
    i = 1
    for benefit in soup.findAll(SPAN, attrs={CLASS: 'sr-only'}):
        title = benefit
        desc = benefit.findNext(H1, attrs={CLASS: 'h4 bold'})
        benefits[(CAL_CASHBACK_STR, title.text.strip())] = desc.text.strip()
        i += 1


def americanexpress_scraper(benefits):
    driver = webdriver_unit()
    driver.get(URL_AMERICANEXPRESS)
    XPATH = '//*[@id="ctl00_MainPlaceHolder_ctlBenefitSearch_divSearchFilterCards"]/div[2]/a'
    all_button = driver.find_element_by_xpath(XPATH)
    all_button.click()
    time.sleep(1)
    i = 1
    page_number = 1
    try:
        while True:
            soup = BeautifulSoup(driver.page_source, HTML_PARSER)
            for benefit in soup.findAll('div', attrs={'class': 'SearchSimpleImageTitle'}):
                title = benefit.text
                desc = title
                benefits[(AMERICANEXPRESS_STR, str(i) + '. ')] = desc
                i += 1
            page_number += 1
            next_page_xpath = '//*[@id="ctl00_MainPlaceHolder_ctlBenefitSearch_divSearchContent"]/div[23]/span[' + str(
                page_number) + ']/a'
            # WebDriverWait(driver, 3).until(EC.presence_of_element_located(By.XPATH, next_page_xpath))
            next_page_button = driver.find_element_by_xpath(next_page_xpath)
            next_page_button.click()
            time.sleep(1)
    except NoSuchElementException:
        return
    except StaleElementReferenceException:
        return
    except ElementNotVisibleException:
        return


def cal_scraper(benefits):
    driver = webdriver_unit(True)
    driver.get(URL_CAL)
    SELECTOR_XPATH = '//*[@id="Category_listbox"]/li[28]/a'
    ALL_XPATH = '//*[@id="Category.0"]'
    selector = driver.find_elements_by_xpath(SELECTOR_XPATH)
    pass


if __name__ == '__main__':
    scraper()
