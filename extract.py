#This script scrapes the previous day files from SGX website, since SGX updates their website the next day. 
#Running it on the 12 Aug 2020 will give you files from 11 Aug 2020
import requests
import pandas as pd
import os
import time
import argparse
import shutil
import datetime as dt
import numpy as np
import logging 
import sys

from configparser import ConfigParser
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from datetime import date, timedelta
from datetime import datetime

def check_market_day(input_date):
    weekno = input_date.weekday()
    if weekno > 5:
        return False
    else:
        return True

def get_date_id(reference_date,reference_id,offset,input_date):
    #Use a reference date and ID taken from config file, moving forward if it detects that a file is also available on a weekend add +1 to offset and fields are updated 
    reference_date = datetime.strptime(reference_date, '%d-%m-%Y').date()
    count = np.busday_count(input_date,reference_date)
    date_id = int(reference_id) - count + int(offset)
    
    return date_id

def main(args):

    #log = logging.basicConfig(filename='./logs/extract.logs',level= logging.WARNING, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    file_handler = logging.FileHandler(filename='./logs/tmp.log')
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO, 
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )

    logger = logging.getLogger('LOGGER_NAME')


    config.read(args.cfg)
    website = config['website']['sgx_website']
    download_link = config['download_link']['dl_url']

    reference_date = config['reference_date']['date']
    reference_id = config['reference_date']['id']
    offset = config['reference_date']['offset']

    
    #Check if user input in the correct DD-MM-YYYY format 
    if args.datestring:
        input_dates_list = [str(item) for item in args.datestring.split(',')]
        format_dates_list = []
        for dates in input_dates_list:
            try:
                check_date = datetime.strptime(dates, '%d-%m-%Y').date()
                format_dates_list.append(check_date)
            except:
                logger.info('Incorrect data format:' + str(dates)+ ' , should be in DD-MM-YYYY')
        if len(format_dates_list)>= 1:
            date_list = [datetime.strftime(date,"%d %b %Y") for date in format_dates_list ]
            logger.info('Date list:' + str(date_list))
        else:
            return logger.info('There are no dates input that is in the correct format, exiting script')
    else:
        logger.info('Downloading yesterday files now')
        yesterday = dt.date.today() - timedelta(days=1)
        yesterday = yesterday.strftime("%d %b %Y")
        date_list = [yesterday]


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
        logger.warning('Downloading correct webdriver version to run driver, please install latest version and add to folder for easier use')
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)

    try:
        driver.get(website)
        time.sleep(7)
    except:
        logger.error("Incorrect website link given please check link and run script again")

    #Initialize elements on website 
    data_type = driver.find_elements_by_name('type')
    date_type = driver.find_elements_by_name('date')
    download_button = driver.find_elements_by_tag_name('button')

    if len(data_type) == 0:
        logger.critical("Unable to locate type of data element on website")
    if len(date_type) == 0:
        logger.critical("Unable to locate date element on website")
    if len(download_button) == 0:
        logger.critical("Unable to locate download element on website")

    data_type = data_type[0]
    date_type = date_type[0]
    
    #Get dates available from website 
    date_type.click()
    time.sleep(5)
    date_options = driver.find_elements_by_class_name('rows-container')
    date_available = date_options[0].text
    date_avail = date_available.split('\n')
    date_type.click()

    #Iterate through all input dates
    # for date in date_list:
    #     if date in date_avail:
    #         date_idx = date_avail.index(date)
    #         time.sleep(2)
    #         date_type.click()
    #         time.sleep(5)
    #         date_element = driver.find_elements_by_name('sgx-select-picker-value')
    #         if len(date_element) == 0:
    #             logger.critical("Date element from drop down list was not located")
    #         date_element[date_idx].click()
        
    #         for data_idx in range(4):
    #             data_type.click()
    #             time.sleep(5)
    #             data_element = driver.find_elements_by_name('sgx-select-picker-value')[data_idx]
    #             if len((driver.find_elements_by_name('sgx-select-picker-value'))) == 0:
    #                 logger.critical("Type of data element from drop down list was not located")
    #             data_element.click()
    #             download_button[0].click()
    
    for date in date_list:
        if date in date_avail:
            date_idx = date_avail.index(date)
        
            for data_idx in range(4):
                data_type.click()
                time.sleep(5)
                data_element = driver.find_elements_by_name('sgx-select-picker-value')[data_idx]
                if len((driver.find_elements_by_name('sgx-select-picker-value'))) == 0:
                    logger.critical("Type of data element from drop down list was not located")
                data_element.click()
                date_type.click()
                time.sleep(5)
                date_element = driver.find_elements_by_name('sgx-select-picker-value')
                if len(date_element) == 0:
                    logger.critical("Date element from drop down list was not located")
                date_element[date_idx].click()
                download_button[0].click()
            
            #Updating config file if it is a weekend and files were available
            current_obj = datetime.strptime(date,"%d %b %Y").date()
            if check_market_day(current_obj) == False:
                new_date_id = get_date_id(reference_date,reference_id,offset,current_obj)
                new_offset = offset + 1
                new_date = datetime.strftime(current_obj,'%d-%m-%Y').date()
                new_date_id += 1
                config.set('reference_date','offset', str(new_offset))
                config.set('reference_date','date', str(new_date))
                config.set('reference_date','id', str(new_date_id))
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

            #Wait for all files to finish downloading
            time.sleep(10) 
            
            if not os.path.exists('./Downloads/' + str(date)):
                os.makedirs('./Downloads/'+ str(date))
            
            
            #Overwrite the files if it has already been downloaded in folder
            files = os.listdir(download_dir)
            dest = './Downloads/' + str(date)
            for f in files:
                if (f.startswith('TC') or f.startswith('Tick') or f.startswith('WEBPXTICK')):
                    if os.path.exists(dest + '/' + f):
                        print('A file already exists in the folder, overwriting with the latest file')
                        os.remove(dest+ '/' + f)
                    shutil.move(download_dir+'/'+ f,dest)
                    logger.info(str(f) + ' has been successfully downloaded')

        else:
            latest_date_str = date_avail[0]
            latest_date_object = datetime.strptime(latest_date_str,"%d %b %Y").date()

            smallest_date_str = date_avail[-1]
            smallest_date_object = datetime.strptime(smallest_date_str,"%d %b %Y").date()

            date_obj = datetime.strptime(date,"%d %b %Y").date()
            #Compare dates if input date > website latest date available, this means that website has not been updated yet today
            if date_obj > latest_date_object:
                if check_market_day(date_obj) == False:
                    logger.info('The file has not been updated or uploaded on SGX website, please try again at a later time and run script again manually')
                else:
                    logger.info('Date falls on a weekend, no files are available for download')
            elif date_obj >= smallest_date_object and date_obj <= latest_date_object:
                logger.info('No files were generated on SGX website on this day, please check if it was a market day')
            elif check_market_day(date_obj) == False:
                logger.info('Your input date falls on a weekend,  please input a date that falls on a weekday')
            else:
                #Date input was more than 5 market days back , unable to scrape directly from SGX website.
                if not os.path.exists('./Downloads/' + str(date)):
                    os.makedirs('./Downloads/'+ str(date))
            
                date_id = get_date_id(reference_date,reference_id,offset,date_obj)

                files_list = ['WEBPXTICK_DT.zip','TC_structure.dat','TC.txt','TickData_structure.dat']

                for files in files_list:
                    url = download_link + str(date_id) + '/' + str(files)
                    r = requests.get(url)
                    date_str = datetime.strftime(date_obj,"%Y%m%d")
                    if files == 'WEBPXTICK_DT.zip':
                        f_file = 'WEBPXTICK_DT-' + str(date_str) + '.zip'
                        with open('./Downloads/'+ str(date) + '/' + str(f_file) , 'wb') as f:
                            f.write(r.content)
                            if os.path.getsize('./Downloads/'+ str(date) + '/' + str(f_file)) < 10000:
                                logging.warning("File may be empty, please check the download link structure again")
                    if files == 'TC.txt':
                        f_file = 'TC_' + str(date_str) + '.txt'
                        with open('./Downloads/'+ str(date) + '/' + str(f_file) , 'wb') as f:
                            f.write(r.content)
                    if files == 'TC_structure.dat' or files == 'TickData_structure.dat':
                        with open('./Downloads/'+ str(date) + '/' + str(files) , 'wb') as f:
                            f.write(r.content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--datestring', type=str, metavar='', help = ''''DD-MM-YYY,DD-MM-YYY' delimited string input''')
    parser.add_argument('--cfg', type=str, metavar= '', help='Config file directory', default= './config.ini' )
    args = parser.parse_args()
    config = ConfigParser()
    main(args)
