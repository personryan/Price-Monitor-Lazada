#####################################################################################################
# Version No | Date of Edit   | Edited By       |      Remarks                                      #
# ------------------------------------------------------------------------------------------------- #
#   v 1.0    | 15 - 10 - 2021 | Ariff/Lay Kiat  | Initial file                                      #
#   v 1.1    | 24 - 10 - 2021 | Ariff/Lay Kiat  | Using DB fetch URLs                               #
#   v 1.2    | 24 - 10 - 2021 | Ariff/Lay Kiat  | Added update to URL valid                         #
#   v 1.3    | 22 - 10 - 2021 | Ariff/Lay Kiat  | inserted cookie to allow scrape without error 429 #
#   v 1.4    | 27 - 10 - 2021 | Bruce           | Update and consolidate functions, add more checks #
#                                                 for price and rating cleaning. Allows scrapping   #
#                                                 of redmart seller, add errorhandler               #
#####################################################################################################
import glob
import os
from bs4 import BeautifulSoup
import requests
from csv import writer
from datetime import datetime
import pandas as pd
from time import sleep
from Resource import sqlCommand
from Resource import errorHandler
import configparser

#Fetch details from properties.ini
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
textToRemovePath = config['TEXT_TO_REMOVE_PATH']['path']
scrapeDataPath = config['DATA_PATH']['scrapepath']
cleanDataPath = config['DATA_PATH']['cleanpath']

def create_filename():
    '''create_filename: Get current datetime as filename'''
    # prepare newFileName as the current date time
    file_name = datetime.now()
    # Removes microseconds and changes output to be YYYY-MM-DDTHHMMSS, cannot have ":" between HHMMSS
    file_name = str(file_name.replace(microsecond=0)).replace(" ", "T").replace(":", "")
    return file_name

def remove_extra_char(ds, column_input, unwanted_chars):
    '''remove_extra_char:arg1 = raw data, arg2 = column, arg3 = unwanted char'''
    ds[column_input] = ds[column_input].str.replace(r'\W', ' ', regex=True).astype(str)
    ds[column_input] = ds[column_input].replace(to_replace=unwanted_chars, value='', regex=True)
    return ds

def rating_cleaner(data_set, column_of_rating):
    '''rating_cleaner:Func strips "Ratings" and replaces "No" to 0 so list will be all numbers'''
    rating_list = []
    for w in list(data_set[column_of_rating]):
        w = w.replace(" Ratings", "")
        w = w.replace("No", "0")
        if not w.isdigit():
            w = w.replace(w, "0")
        w = w.strip()
        rating_list.append(w)
    data_set[column_of_rating] = rating_list
    return data_set

def category_cleaner(data_set, column_of_category):
    '''category_cleaner:Func to split values as format is More "desired category" from xxx, so func will return "desired category"'''
    category_list = list(data_set[column_of_category])
    for items in range(0, len(category_list)):
        raw = category_list[items]
        first_strip = raw.split("More ")[1]
        second_strip = first_strip.split(" from")[0]
        third_strip = second_strip.strip()
        category_list[items] = third_strip
    data_set[column_of_category] = category_list
    return data_set

def price_cleaner(data_set, column_of_price):
    '''price_cleaner:Func to remove $ and , signs leaving behind digits.decimal'''
    price_list = []
    for w in list(data_set[column_of_price]):
        w = w.replace("$", "")
        w = w.replace(",", "")
        if not w.replace(".","").isdigit():
            w = w.replace(w, "0")
        w = w.strip()
        price_list.append(w)
    data_set[column_of_price] = price_list
    return data_set

def retrieve_headers():
    '''retrive_headers: returns a list of headers to be used for the dataframe'''
    headers = ['Item', 'Brand', 'Seller', 'Category', 'Price', 'Ratings', 'URLId']
    return headers

def update_valid_url(con, urlId, lists):
    '''update_valid_url: Update URL validity'''
    table = "url"
    condition = "urlid=" + str(urlId)
    # If list is not empty, update valid to 1 (valid scrape) else 2 (invalid scrape)
    if lists:
        sqlCommand.sql_update(con, "valid=1", table, condition)
    else:
        sqlCommand.sql_update(con, "valid=2", table, condition)

def get_text_to_remove():
    '''get_text_to_remove: Get the list of text to remove'''
    # Declare list for text to remove
    textToRemoveList = []

    # Open text to remove file and append text into a list
    file = open(textToRemovePath, encoding='utf-8-sig')
    for line in file:
        textToRemoveList.append(line.strip('\n'))

    return textToRemoveList;

def scrape_URL(database):
    '''scrapeURL: Use to scrape information from the URL'''
    #Setting up sql connection
    con = sqlCommand.sql_connection(database)

    #Getting URL List where valid is not equal to 2(2 is url invalid)
    urlList = sqlCommand.sql_get_all(con,"url","valid != 2")

    #Creating a new .csv for the output of scraped dat
    fileName = create_filename()
    file = open(scrapeDataPath+fileName+'.csv', 'w', encoding='utf8', newline='')

    #Open writer to write into file
    fileWriter = writer(file)

    #Set up header to write into
    header = retrieve_headers()
    fileWriter.writerow(header)

    #Fetching the URLs to be scraped from DB
    for urlRow in urlList:
        #Set urlRow to variable
        urlId = urlRow[0]
        url = urlRow[1]
        urlValid = urlRow[2]

        print("Currently Scrapping: "+url)
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            #Check response code
            if(page.ok):
                print("Response OK! Starting to scrape...")
                lists = soup.find_all('div', class_="pdp-block pdp-block__main-information-detail")
                #Update validity of URL based on retrieve list
                if(urlValid==0):
                    update_valid_url(con, urlId, lists)
                    if not lists:
                        print("Error! Link is not valid for scrapping")

                # Refine the search to scrape for specific element within the above div class to get item details, like name, price and ratings
                for list in lists:
                    itemName = list.find('h1', class_="pdp-mod-product-badge-title").text.replace('\n', '')
                    itemPrice = list.find('span', class_="pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl").text.replace('\n', '')
                    itemRating = list.find('a', class_="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-review-summary__link").text.replace('\n', '')
                    itemBrand = list.find('a', class_='pdp-link pdp-link_size_s pdp-link_theme_blue pdp-product-brand__brand-link').text.replace('\n', '')
                    itemCategory = list.find('a', class_="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-product-brand__suggestion-link").text.replace('\n', '')
                    itemSeller = list.find('a', class_='pdp-link pdp-link_size_l pdp-link_theme_black seller-name__detail-name')

                    #For when redmart is the seller since they use logo as the seller instead of text
                    if not itemSeller:
                        if (list.find('div', class_='pdp-redmart-seller')):
                            itemSeller = "RedMart"
                        else:
                            itemSeller = "None"
                    else:
                        itemSeller = itemSeller.text.replace('\n', '')

                    info = [itemName, itemBrand, itemSeller, itemCategory, itemPrice, itemRating, urlId]

                    # The writer will then export all the scraped data into the .csv
                    fileWriter.writerow(info)
                    print("Information has been added into CSV!")

            else:
                print("Response FAIL "+str(requests.status_codes)+"! Skipping this link...")
        except Exception as e:
            errorHandler.writeLogs(str(e))

        #Delay scrapping so not suspicious
        sleep(5)

    #close file and connection
    con.close()
    file.close()
    print("All links has been scrapped!")

def clean_scrape_file():
    '''clean_scrape_file: func to clean out unwanted text and strings'''
    header = retrieve_headers()
    itemsToRemove = get_text_to_remove()
    for filename in glob.glob(os.path.join(scrapeDataPath, '*.csv')):
        try:
            rawFilename = os.path.basename(filename)
            print("Currently cleaning: "+rawFilename)

            #Open csv to dataframe and clean the text
            dataFrame = pd.read_csv(filename)
            dataFrame = remove_extra_char(dataFrame, header[0], itemsToRemove)
            dataFrame = category_cleaner(dataFrame, header[3])
            dataFrame = price_cleaner(dataFrame, header[4])
            dataFrame = rating_cleaner(dataFrame, header[5])
            dataFrame.to_csv(filename, index=False)

            print("CSV has been cleaned!")
            print("Moving file to cleanData....")
            os.rename(filename,cleanDataPath+rawFilename)
        except Exception as e:
            errorHandler.writeLogs(str(e))
            errorHandler.moveErrorFile(filename)
    print("All CSV file has been cleaned!")