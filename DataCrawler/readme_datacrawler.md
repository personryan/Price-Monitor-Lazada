DataCrawler

Author: Bruce Wang
DateOfEdit: 28-10-2021

Hi welcome to the DataCrawler subfolder!
In this folder you will find 2 files,

1. main.py
2. dataPreProcessing.py

main.py is our main function which we call to run the data crawling process.

dataPreProcessing.py is our module file where it store functions used for
scrapping and cleaning.

In dataPreProcessing, our two main functions would be
1. scrape_URL()
2. clean_scrape_file()

scrape_URL handles the scraping of URL using beautifulsoup4, currently
we are only able to handle products that are from Lazada. The URL to scrape
is being stored in a database. We will be retrieving the following from a 
product page in lazada
1. Item name
2. Brand
3. Seller
4. Category
5. Price
6. Rating
After scraping, the data scrape will be written into a CSV stored in Data\ScrapeData.
This file will be named after the datetime where the scrapping start.

After scrapping process is done, clean_scrape_file will be called to handle
the cleaning of CSV. It will read the CSV with pandas and put into a dataframe.
This dataframe will then be pass to other functions that will clean the data.
For cleaning, we aim to reduce any redundent extra characters that are in the
Item name and also the cleaning and formating of category, price and rating.
After the cleaning process is done, the CSV will be moved into Data\CleanData for
processing.

TAKE NOTE: Only main.py is meant to be run, the other python file is use as a import

Acknowledgement
Ariff was in charge of the scrapping of URL and LayKiat was in charge of cleaning the
scrape CSV. This was done concurrently on 2 different python file before it was
combine into dataPreProcessing.py. Bruce then took over the file to clean up and
ensure that it's able to work with the other modules.