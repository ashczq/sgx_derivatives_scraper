import bs4
import requests
import urllib
import random
import pandas as pd

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from datetime import date
from datetime import datetime

def main():
    url = 'https://www.mom.gov.sg/employment-practices/public-holidays'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    request = urllib.request.Request(url,headers={'User-Agent': user_agent})
    response = urllib.request.urlopen(request)

    page_soup = soup(response,'html.parser')
    dates = page_soup.findAll("span", {"class":'text-date-mobile'})


    formatted_dates = []
    for date in dates:
        append_dates = date.text.split(',')[0].split('-')
        for item in append_dates:
            if item[0] == ' ':
                format_item = datetime.strptime(item," %d %B %Y").date()
                formatted_dates.append(format_item)
            elif item[-1] == ' ':
                format_item = datetime.strptime(item,"%d %B %Y ").date()
                formatted_dates.append(format_item)
            else:
                format_item = datetime.strptime(item,"%d %B %Y").date()
                formatted_dates.append(format_item)

    my_dict = {'Holidays': formatted_dates}
    df = pd.DataFrame(my_dict)

    df.to_csv('./Holidays.csv',index=False)

if __name__ == '__main__':
    main()