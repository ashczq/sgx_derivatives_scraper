import requests
import pandas as pd
import os
import time
import argparse

from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from datetime import date
from datetime import datetime

def check_market_day(input_date,hol_list):
    weekno = input_date.weekday()
    if weekno > 5:
        print('This date is a weekend, the SGX market is not open')
    elif input_date in hol_list:
        print('This date is a Public Holiday, the SGX market is not open')
    else:
        return True

def main(args):

    #Get dataframe for public holidays and store in list
    df = pd.read_csv('./Holidays.csv')
    holiday_dates = list(df['Holidays'].values)
    holiday_datetime = []
    for date in holiday_dates:
        item = datetime.strptime(date,'%Y-%m-%d').date()
        holiday_datetime.append(item)
    
    #Need to check if it is a market day when user inputs 
    if args.datestring:
        dates_list = [str(item) for item in args.datestring.split(',')]
        format_dates_list = [datetime.strptime(date, '%d-%m-%Y').date() for date in dates_list]
        date_list = [datetime.strftime(date,"%d %b %Y") for date in dates_list ]
        #print(date_list)
    else:
        if check_market_day(datetime.today(),holiday_datetime) == True:
            date_list = [date.today().strftime("%d %b %Y")]
            #print(date_list)
        else:
            return check_market_day(datetime.today(),holiday_datetime)

    chrome_options = webdriver.ChromeOptions()
    download_dir = os.getcwd() + '/Downloads'
    preferences = {"download.default_directory": download_dir ,
                "directory_upgrade": True,
                "safebrowsing.enabled": True }
    chrome_options.add_experimental_option("prefs", preferences)
    
    try:
        PATH = './chromedriver'
        driver = webdriver.Chrome(executable_path=PATH,chrome_options=chrome_options)
    except:
        print('Downloading correct webdriver version to run driver')
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)

    driver.get("https://www.sgx.com/research-education/derivatives")
    time.sleep(7)

    #get dates available 
    date_type = driver.find_elements_by_class_name('rows-container')
    date_type.click()
    time.sleep(2)
    date_available = date_type[0].text
    date_avail = date_available.split('\n') #list of date strings pulled from sgx website
    
    #initialize elements on website 
    data_type = driver.find_element_by_name('type')
    download_button = driver.find_elements_by_tag_name('button')
    date_type = driver.find_element_by_name('date')
    
    #loop through user input date string list
    for date in date_list:
        if date in date_avail:
            date_idx = date_avail.index(date)
            date_type.click()
            time.sleep(2)
            date_element = driver.find_elements_by_name('sgx-select-picker-value')
            date_element[date_idx].click()
        
            for data_idx in range(4):
                data_type.click()
                time.sleep(2)
                data_element = driver.find_elements_by_name('sgx-select-picker-value')[data_idx]
                data_element.click()
                download_button[0].click()
        else:
            latest_date_str = date_avail[0]
            latest_date_object = datetime.strptime(latest_date_str,"%d %b %Y").date()
            date_obj = datetime.strptime(date,"%d %b %Y").date()
            #compare dates if input date > website latest date , this means that website has not been updated yet today
            if date_obj > latest_date_object:
                print('The file has not been updated or uploaded on SGX website, please try again at a later time')
            else:
                #run algo to get files more than 5 days ago
                


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--datestring', type=str, metavar='', help = ''''DD-MM-YYY,DD-MM-YYY' delimited string input''')
    args = parser.parse_args()
    main(args)
