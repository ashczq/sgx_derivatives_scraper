import os
import pandas as pd
import numpy as np
import time
import datetime as dt
import requests 
import argparse
import logging

from datetime import date
from datetime import datetime

def get_date_id(input_date):
    #Use 10 Aug 2020 , ID = 4697 as a reference point
    reference_date = datetime(2020,8,10).date()
    count = np.busday_count(input_date,reference_date)
    date_id = 4697 - count
    
    return date_id

def check_market_day(input_date):
    weekno = input_date.weekday()
    if weekno > 5:
        #print('This date is a weekend, the SGX market is not open')
        #print(weekno)
        return False
    else:
        #print(weekno)
        return True

def main(args):
    #Get dataframe for public holidays and store in list
    # df = pd.read_csv('./Holidays.csv')
    # holiday_dates = list(df['Holidays'].values)
    # holiday_datetime = []
    # for date in holiday_dates:
    #     item = datetime.strptime(date,'%Y-%m-%d').date()
    #     holiday_datetime.append(item)
    

    if args.datestring:
        date_list = [str(item) for item in args.datestring.split(',')]
        dates_list = [datetime.strptime(date, '%d-%m-%Y').date() for date in date_list]
        #date_list = [datetime.strftime(date,"%d %b %Y") for date in dates_list ]
        #print(dates_list)
    else:
        yesterday = dt.date.today() - dt.timedelta(days=1)
        dates_list = [yesterday]
        #print(dates_list)
    
    for input_date in dates_list:
        if check_market_day(input_date) == True:
            
            if not os.path.exists('./Downloads/' + str(input_date)):
                os.makedirs('./Downloads/'+ str(input_date))
            
            date_id = get_date_id(input_date)

            files_list = ['WEBPXTICK_DT.zip','TC_structure.dat','TC.txt','TickData_structure.dat']

            for file in files_list:
                url = 'https://links.sgx.com/1.0.0/derivatives-historical/' + str(date_id) + '/' + str(file)
                r = requests.get(url)
                with open('./Downloads/'+ str(input_date) + '/' + str(file) , 'wb') as f:
                    f.write(r.content)
        else:
            #invalid date or non market day
            if check_market_day(input_date) == False:
                print('This date falls on a non-market day, the SGX market is not open')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--datestring', type=str, metavar='', help = ''''DD-MM-YYY,DD-MM-YYY' delimited string input''')
    args = parser.parse_args()
    main(args)
