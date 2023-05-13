###########################################################################################################
# Version No | Date of Edit | Edited By | Remarks                                                         #
#---------------------------------------------------------------------------------------------------------#
#   v 1.0    |  14-10-2021  |  Bruce W  | Initial File                                                    #
#   v 1.1    |  14-10-2021  |  Bruce W  | Change the price generator                                      #
#   v 1.2    |  22-10-2021  |  Bruce W  | Update price calculation                                        #
###########################################################################################################
import csv
import os
from csv import writer
from datetime import datetime, timedelta
from random import choices

# Open to read
file = open('..\\Data\\CleanData\\2021-10-28T172831.csv', 'r', encoding='utf8', newline='')
rawFilename = os.path.basename(file.name).split(".")[0]
csvreader = csv.reader(file)
header = next(csvreader)
baselist = list(csvreader)
file.close()

datetime_str = rawFilename.split("T")
fulldate = datetime_str[0]
time = datetime_str[1]

def generateNewRatings(rating,i):
    rating = int(rating)
    if rating < 10:
        return int(float(rating) - (float(i)*0.002))
    elif rating < 50:
        return int(float(rating) - (float(i)*0.02))
    elif rating < 100:
        return int(float(rating) - (float(i)*0.05))
    elif rating < 150:
        return int(float(rating) - (float(i)*0.1))
    elif rating < 200:
        return int(float(rating) - (float(i)*0.24))
    elif rating < 250:
        return int(float(rating) - (float(i)*0.38))
    elif rating < 300:
        return int(float(rating) - (float(i)*0.48))
    elif rating > 350:
        return int(float(rating) - (float(i)*0.9))
    return rating

def generateNewPrice(price,i,month,day):
    standard_population = [1, 0.97, 0.95, 0.90, 0.86]
    standard_weight = [0.99, 0.01, 0.01, 0.01, 0]
    sales_weight = [0.5, 0.25, 0.3, 0.1, 0.05]
    price = float(price)
    i = int(i)
    standard_randomiser = choices(standard_population,standard_weight)[0]
    sales_randomiser = choices(standard_population,sales_weight)[0]
    #electronics outdate hence price drop
    if (i > 180):
        price = price * 1.02

    if month == day:
        price *= sales_randomiser
    else:
        price *= standard_randomiser

    return price

for i in range(1,30,1):
    #Copy CSV content over to write
    newlist = baselist.copy()

    #Preparing the date for filename
    d = datetime.strptime(fulldate,'%Y-%m-%d')- timedelta(days=i)
    newDate = d.date()
    newFileName = str(newDate)+"T"+time

    #Filename = date - 1
    newFile = open('..\\Data\\CleanData\\'+newFileName+'.csv', 'w+', encoding='utf8', newline='')
    print("Creating a new CSV:"+newFileName, end=".....")
    thewriter = writer(newFile)
    thewriter.writerow(header)

    #Writing content into the new CSV
    for itemInfo in newlist:
        # Set the items to the respective variable
        name = itemInfo[0]
        brand = itemInfo[1]
        sellerName = itemInfo[2]
        categoryName = itemInfo[3]
        url = itemInfo[6]

        price = itemInfo[4]
        price = generateNewPrice(price,i, newDate.month,newDate.day)

        rating = itemInfo[5]
        if not rating == 0:
            rating = generateNewRatings(rating,i)

        info = [name, brand, sellerName, categoryName, price, rating,url]
        thewriter.writerow(info)

    newFile.close()
    print("CSV created! Total Count: %d"%i)


