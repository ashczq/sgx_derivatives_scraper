==============================

Author: Ashley Chan Zheng Qun

Application for data engineer position at Dynamic Technology Lab

Writeup of assignment available under reports/writeup.docx

------------

## Requirements

Python 3.6 or later with all requirements.txt dependencies installed, including. To install run:
```bash
$ pip install -r requirements.txt
```
Please check your chrome version and download the correct version of chromewebdriver from: https://chromedriver.chromium.org/downloads for ease of use
else the script would automatically download the correct version each time. 

## Simple usage
By default, running the script will use yesterday's date. To run: 
```bash
$ python extract.py 
```
```bash
$ python extract.py --datestring DD-MM-YYYY,DD-MM-YYYY 
```

## Config file

The config files should not be edited unless the URL links have changed. Please check SGX website if downloading of files fail and update in config file
accordingly at /config.ini


## Files

Default download directory would be in /Downloads and logs will be in /logs/tmp.log


## Contact

For feedback and bugs:

Email: ashczq@gmail.com 
