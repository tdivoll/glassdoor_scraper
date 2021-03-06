#Requires selenium and pandas

import time
import pandas as pd
from argparse import ArgumentParser
import argparse
import logging
import logging.config
from selenium import webdriver as wd
from selenium.webdriver.support.ui import Select
import selenium
import numpy as np
from schema import SCHEMA
import json
import urllib
import datetime as dt
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
#Inputs
#page url is the ***Review*** page of the company. 
#******DO NOT INCLUDE the .htm**************
csv_save_folder = "../Output CSV/"
company_name_list = ["Wells Fargo", "Apple", "Ford Motor Company"]
#Number at the end of the reviews page. May be a way to automate this but will leave that to your own time
company_number_list = ["E8876", "E1138", "E263"]
#Limit is number of reviews to load (code is currently not robust to end point so limit needs to be smaller than the total number of reviews)
LIMIT = 5
#Your glassdoor username and password
USERNAME = ''
PASSWORD = ''
#headless means the web browser wont ope up


HEADLESS = True
#SORT_OPTION = NA will default to Popular. Otherwise can input to sort by:
#		-Popular
#		-Hishest Rating
#		-Lowest Rating
#		-Most Recent
#		-Oldest First
SORT_OPTION = "NA" 
#					
SORT_OPTION = "Most Recent"
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
#_______________________________________________________________________________________________________________________________________
if PASSWORD == '': 
	print("You need to input a username and password into the code")



args = argparse.Namespace(credentials=None, headless=HEADLESS, limit=LIMIT, max_date=None, min_date=None, password=PASSWORD,
                 start_from_url=True, username=USERNAME, sort_option=SORT_OPTION)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(lineno)d\
    :%(filename)s(%(process)d) - %(message)s')
ch.setFormatter(formatter)

logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.CRITICAL)


def scrape(field, review, author):
    def scrape_full_text(review):
        # print(review.text)
        return review.text

    def scrape_date(review):
        return review.find_element_by_tag_name(
            'time').get_attribute('datetime')

    def scrape_emp_title(review):
        if 'Anonymous Employee' not in review.text:
            try:
                res = author.find_element_by_class_name(
                    'authorJobTitle').text.split('-')[1]
            except Exception:
                # logger.warning('Failed to scrape employee_title')
                res = np.nan
        else:
            res = np.nan
        return res

    def scrape_location(review):
        if 'in' in review.text:
            try:
                res = author.find_element_by_class_name(
                    'authorLocation').text
            except Exception:
                res = np.nan
        else:
            res = np.nan
        return res

    def scrape_status(review):
        try:
            res = author.text.split('-')[0]
        except Exception:
            # logger.warning('Failed to scrape employee_status')
            res = np.nan
        return res

    def scrape_rev_title(review):
        return review.find_element_by_class_name('summary').text.strip('"')
    #These had bad element selectors. We can always come back and code them better, but have currently just dumped the full text into the csv
    # def scrape_years(review):
    #     ##Added to fix termination issue
    #     try:
    #         first_par = review.find_element_by_class_name(
    #             'reviewBodyCell').find_element_by_tag_name('p')
    #     except:
    #         # logger.warning('Failed to scrape year')
    #         return np.nan
    #     ##
    #     if '(' in first_par.text:
    #         res = first_par.text[first_par.text.find('(') + 1:-1]
    #     else:
    #         res = np.nan
    #     return res

    # def scrape_helpful(review):
    #     try:
    #         helpful = review.find_element_by_class_name('helpfulCount')
    #         res = helpful[helpful.find('(') + 1: -1]
    #     except Exception:
    #         res = 0
    #     return res

    def expand_show_more(section):
        try:
            more_content = section.find_element_by_class_name('moreContent')
            more_link = more_content.find_element_by_class_name('moreLink')
            more_link.click()
        except Exception:
            pass

    # def scrape_pros(review):
    #     try:
    #         pros = review.find_element_by_class_name('pros')
    #         expand_show_more(pros)
    #         res = pros.text.replace('\nShow Less', '')
    #     except Exception:
    #         res = np.nan
    #     return res

    # def scrape_cons(review):
    #     try:
    #         cons = review.find_element_by_class_name('cons')
    #         expand_show_more(cons)
    #         res = cons.text.replace('\nShow Less', '')
    #     except Exception:
    #         res = np.nan
    #     return res

    # def scrape_advice(review):
    #     try:
    #         advice = review.find_element_by_class_name('adviceMgmt')
    #         expand_show_more(advice)
    #         res = advice.text.replace('\nShow Less', '')
    #     except Exception:
    #         res = np.nan
    #     return res

    def scrape_overall_rating(review):
        try:
            ratings = review.find_element_by_class_name('gdStars')
            overall = ratings.find_element_by_class_name(
                'rating').find_element_by_class_name('value-title')
            res = overall.get_attribute('title')
        except Exception:
            res = np.nan
        return res

    def _scrape_subrating(i):
        try:
            ratings = review.find_element_by_class_name('gdStars')
            subratings = ratings.find_element_by_class_name(
                'subRatings').find_element_by_tag_name('ul')
            this_one = subratings.find_elements_by_tag_name('li')[i]
            res = this_one.find_element_by_class_name(
                'gdBars').get_attribute('title')
        except Exception:
            res = np.nan
        return res

    def scrape_work_life_balance(review):
        return _scrape_subrating(0)

    def scrape_culture_and_values(review):
        return _scrape_subrating(1)

    def scrape_career_opportunities(review):
        return _scrape_subrating(2)

    def scrape_comp_and_benefits(review):
        return _scrape_subrating(3)

    def scrape_senior_management(review):
        return _scrape_subrating(4)

    funcs = [
        scrape_full_text,
        scrape_date,
        scrape_emp_title,
        scrape_location,
        scrape_status,
        scrape_rev_title,
        # scrape_years,
        # scrape_helpful,
        # scrape_pros,
        # scrape_cons,
        # scrape_advice,
        scrape_overall_rating,
        scrape_work_life_balance,
        scrape_culture_and_values,
        scrape_career_opportunities,
        scrape_comp_and_benefits,
        scrape_senior_management
    ]

    fdict = dict((s, f) for (s, f) in zip(SCHEMA, funcs))

    return fdict[field](review)


def extract_from_page():

    def is_featured(review):
        try:
            review.find_element_by_class_name('featuredFlag')
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def extract_review(review):
        author = review.find_element_by_class_name('authorInfo')
        res = {}
        # import pdb;pdb.set_trace()
        for field in SCHEMA:
            res[field] = scrape(field, review, author)

        assert set(res.keys()) == set(SCHEMA)
        return res

    # logger.info(f'Extracting reviews from page {page[0]}')

    res = pd.DataFrame([], columns=SCHEMA)

    reviews = browser.find_elements_by_class_name('empReview')
    logger.info(f'Found {len(reviews)} reviews on page {page[0]}')

    for review in reviews:
        if not is_featured(review):
            data = extract_review(review)
            # logger.info(f'Scraped data for "{data["review_title"]}"\
# ({data["date"]})')
            res.loc[idx[0]] = data
        else:
            logger.info('Discarding a featured review')
        idx[0] = idx[0] + 1


    return res



def go_to_next_page(url):
    page[0] = page[0] + 1
    # logger.info(f'Going to page {page[0]}')   
    browser.get(url+"_P"+str(page[0])+".htm")
    time.sleep(1)




def sign_in():
    logger.info(f'Signing in to {args.username}')

    url = 'https://www.glassdoor.com/profile/login_input.htm'
    browser.get(url)


    email_field = browser.find_element_by_name('username')
    password_field = browser.find_element_by_name('password')
    submit_btn = browser.find_element_by_xpath('//button[@type="submit"]')

    email_field.send_keys(args.username)
    password_field.send_keys(args.password)
    submit_btn.click()

    time.sleep(1)


def get_browser():
    logger.info('Configuring browser')
    chrome_options = wd.ChromeOptions()
    if args.headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('log-level=3')
    browser = wd.Chrome(options=chrome_options)
    return browser


def sort_reviews(option):
    selection_options = Select(browser.find_element_by_id("FilterSorts"))
    selection_options.select_by_visible_text(option)
    logger.info(f'Sorting Data By {args.sort_option}')
    time.sleep(1)

def get_company_reviews(company_name, company_number, csv_file_name):
    page[0] = 1
    idx[0] = 0
    start = time.time()
    logger.info(f'Scraping up to {args.limit} reviews for {company_name}.')

    res = pd.DataFrame([], columns=SCHEMA)



    url = "https://www.glassdoor.com/Reviews/"+company_name.replace(" ","-")+"-Reviews-"+company_number
    browser.get(url+".htm")
    time.sleep(1)
    if args.sort_option != "NA":
        sort_reviews(args.sort_option)


    reviews_df = extract_from_page()
    res = res.append(reviews_df)


    while len(res) < args.limit:
        go_to_next_page(url)
        reviews_df = extract_from_page()
        res = res.append(reviews_df)

    res.to_csv(csv_file_name, index=False, encoding='utf-8')

    end = time.time()
    logger.info(f'Finished in {end - start} seconds')

def get_all_company_reviews(company_name_list, company_number_list, csv_save_folder):
    csv_file_names = [csv_save_folder + company_name + ".csv" for company_name in company_name_list] 

    sign_in()
    for i in range(len(company_name_list)):
    	get_company_reviews(company_name_list[i], company_number_list[i], csv_file_names[i])
    logger.info(f'finished running code!!!')


page = [1]
idx = [0]
browser = get_browser()
get_all_company_reviews(company_name_list, company_number_list, csv_save_folder)