DataProcessing

Author: Bruce Wang
DateOfEdit: 28-10-2021

Hi welcome to the DataProcessing subfolder!
In this folder you will find 3 files,

1. main.py
2. dataProcesser.py
3. alertFunctions.py

main.py is our main function which we call to run the data processing.

dataProcesser.py is our module file where it store functions used for
processing.

Upon calling of dataProcesser, the first thing it will do is call onto
process_file where it will take all CSV files stored inside Data/CleanData
for processing, with every row in the CSV file it call onto process_item
where each row of item will get processed and add into the database. How
we are processing the items is creating a unique id for each unique category,
seller, brand and item. This allows us to reference to the ID to get the name
of what we are looking file. This also allows us to index everything nicely.

In our dataProcesser, we also call upon the alertFunctions.py. The main purpose
of alertFunctions is to check if for the items that is being processed, is there
any alert set for the items where the current price has meet the desired price.
If such alert exist, we will call send an alert to user via their respective
user type. Our two main mode of communication is send_email and send_telegram.
If user set an alert via the GUI, they will receive an alert for email which 
they have entered. If the user set an alert via our Telegram bot, we will
send an alert to the user via Telegram.

TAKE NOTE: Only main.py is meant to be run, the other two python file is use as a import

Acknowledgement
Ariff was in charge of the alertFunctions where Bruce took over. Bruce was
also in charge of the dataProcesser.