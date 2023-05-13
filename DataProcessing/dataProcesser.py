###########################################################################################################
# Version No | Date of Edit | Edited By | Remarks                                                         #
#---------------------------------------------------------------------------------------------------------#
#   v 1.0    |  07-10-2021  |  Bruce W  | Initial File                                                    #
#   v 1.1    |  11-10-2021  |  Bruce W  | Add brand into processItem                                      #
#   v 1.2    |  12-10-2021  |  Bruce W  | Update to interact w Database, remove some function             #
#   v 1.3    |  14-10-2021  |  Bruce W  | Added functions for brand, add brand into some func, rename     #
#            |              |           | getRawFilename to cleanRawFileName for better clarity & remove  #
#            |              |           | writeFile, update cleanText to remove leading & trailing spaces #
#   v 1.4    |  16-10-2021  |  Bruce W  | remove primary key from getxxxxID, auto include in sqlCommand   #
#   v 1.5    |  22-10-2021  |  Bruce W  | add functions for URL related table, create new processItem func#
#   v 1.6    |  27-10-2021  |  Bruce W  | add new processfile function, update minor stuff to work w all  #
#                                       | add error handling, and change ' to " for sql statement         #
###########################################################################################################
import configparser
from Resource import sqlCommand
from Resource import errorHandler
import glob
import os
import csv
import alertFunctions

#Fetch details from properties.ini
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
cleanDataPath = config['DATA_PATH']['cleanpath']
processedDataPath = config['DATA_PATH']['processedpath']

def clean_raw_filename(filename):
    '''clean_raw_filename: Remove any extension from the file to get Raw format.
    Example: Apple.txt -> Apple'''
    splitFilename = filename.split(".",1)
    rawFilename = splitFilename[0].replace(" ","_")
    return rawFilename

def clean_text(textToBeCleaned):
    '''clean_text: Get text, clear white spaces and replace space with _'''
    cleanStr = textToBeCleaned.strip().replace(" ","_")
    return cleanStr

def format_datetime(dateTime):
    '''format_datetime: Format the datetime for storing into logs. Basically
    2021-10-06T143000 into 2021-10-06 14:30:00 and return the formatted string'''
    dateTimeList = dateTime.split('T',1)
    date = dateTimeList[0]
    time = dateTimeList[1]

    #Split time to hours & min then add : inbetween
    timeStr = time[0:2]+":"+time[2:4]+":"+time[4:6]

    return date+" "+timeStr

def convert_to_numinput(text,type):
    '''convert_to_numinput: Try convert input text into number type and return'''
    return type(text)

def get_seller_id(con,sellerName):
    '''get_seller_id v1.2: Get the ID of the seller, if dont exist, create one'''
    table="seller"
    seller_id = sqlCommand.sql_get_id(con,table,"sellername = \""+sellerName+"\"")

    if seller_id == -1: #If seller ID dont exist, create
        return sqlCommand.sql_insert_one(con,"\""+sellerName+"\"",table)
    else:
        return seller_id

def get_category_id(con,categoryName):
    '''get_category_id v1.2: Get the ID of the category, if dont exist, create one'''
    table="category"
    category_id = sqlCommand.sql_get_id(con,table,"categoryname = \""+categoryName+"\"")
    if category_id==-1: #If category ID dont exist, create
        return sqlCommand.sql_insert_one(con,"\""+categoryName+"\"",table)
    else:
        return category_id

def get_brand_id(con,brandName):
    '''get_brand_id v1.3: Get the ID of the brand, if dont exist, create one'''
    table="brand"
    brand_id = sqlCommand.sql_get_id(con,table,"brandname = \""+brandName+"\"")

    if brand_id == -1: #If brand ID dont exist, create
        return sqlCommand.sql_insert_one(con,"\""+brandName+"\"",table)
    else:
        return brand_id

def get_url_id(con,urlLink):
    '''get_url_id v1.5: Get the ID of the URL'''
    table="url"
    url_id = sqlCommand.sql_get_id(con,table,"urllink = \""+urlLink+"\"")
    if url_id == -1: #If seller ID dont exist, create
        return sqlCommand.sql_insert_one(con,"\""+urlLink+"\", '1'",table)
    else:
        return url_id

def get_iteminfo_id(con,categoryId, sellerId, brandId, itemName,urlId):
    '''get_iteminfo_id: Get the ID of the itemInfo, if dont exist, create one'''
    table="iteminfo"
    item_info_id = sqlCommand.sql_get_id(con,table,"categoryid = '"+str(categoryId)+"' AND sellerid = '"+str(sellerId)+
                                         "' AND brandid = '"+str(brandId)+"' AND itemname = '"+itemName+"'")
    if item_info_id==-1: #If itemInfo ID dont exist, create
        value_to_insert = "'"+itemName+"','"+str(urlId)+"','"+str(categoryId)+"','"+str(sellerId)+"','"+str(brandId)+"'"
        return sqlCommand.sql_insert_one(con,value_to_insert,table)
    else:
        return item_info_id

def write_logs(con,data):
    '''write_logs: write the logs into database'''
    table="logs"
    sqlCommand.sql_insert_bulk(con,data,table)

def process_item(con, itemInfo, dateTime):
    '''process_item: Process the item and return the processed Item'''
    # Set the items to the respective variable
    name = itemInfo[0]
    brand = itemInfo[1]
    sellerName = itemInfo[2]
    categoryName = itemInfo[3]
    price = itemInfo[4]
    rating = itemInfo[5]
    urlId = itemInfo[6]

    # Get ID, clean item name, clean price and rating
    itemNameNoSpace = clean_text(name)
    brandId = get_brand_id(con, brand)
    sellerId = get_seller_id(con, sellerName)
    categoryId = get_category_id(con, categoryName)
    itemInfoId = get_iteminfo_id(con, categoryId, sellerId, brandId, itemNameNoSpace, urlId)
    numPrice = convert_to_numinput(price, float)
    numRating = convert_to_numinput(rating, int)

    alertList = alertFunctions.check_alert(con,itemInfoId,numPrice)
    if alertList:
        alertFunctions.send_alert(con, alertList, name, numPrice, urlId)


    return (numPrice, numRating, str(itemInfoId), dateTime)

def process_file(database):
    '''process_file: Func to start processing csv'''

    #Set up SQL connection
    con = sqlCommand.sql_connection(database)

    # Open all CSV File for Data Processing
    for filename in glob.glob(os.path.join(cleanDataPath, '*.csv')):
        rawFilename = os.path.basename(filename)
        print("Currently processing: " + rawFilename)
        try:
            with open(os.path.join(os.getcwd(), filename), 'r', encoding='utf-8-sig') as file:
                # Reading file as CSV
                csvreader = csv.reader(file)
                # Getting items header
                header = next(csvreader)

                # Get the datatime from rawfilename of the file
                rawFilenameNoExt = clean_raw_filename(rawFilename)
                dateTime = format_datetime(rawFilenameNoExt)

                # Declare logs list
                logsData = []

                # Where the magic happens
                for itemInfo in csvreader:
                    processItem = process_item(con, itemInfo, dateTime)
                    # Append logs into a list
                    logsData.append(processItem)

                # Write logs into database
                write_logs(con, logsData)
                print("Logs has been added for this CSV")

            print("Moving file to processedData....")
            os.rename(filename, processedDataPath + rawFilename)
        except Exception as e:
            errorHandler.writeLogs(str(e))
            errorHandler.moveErrorFile(filename)
    # Close the SQL Connection
    con.close()
    print("All CSV file process!")