Resources

Author: Bruce Wang
DateOfEdit: 28-10-2021

Hi welcome to the Resources subfolder!

In this folder you will find 7 files,

1. clean.txt
2. crashlogs.txt
3. errorHandler.py
4. lazada.png
5. pricemonitordatabase.db
6. properties.ini
7. sqlCommand.py

clean.txt is used to store text that will be clean off Item name during the
cleaning of data.

crashlogs.txt logs any error that was faced by our programme during running

errorHandler.py is the python file that is in charge of handling any error faced,
it consists of 2 functions writeLogs and moveErrorFile. writeLogs will write the
error into the crashlogs.txt while moveErrorFile will move the file that is facing
the error into the Data\ErrorData folder for farther investigation

lazada.png is the image we use for our GUI

pricemonitordatabase.db is the database that our application is storing data into

properties.ini contains all the filepath, login information for email and bot token
for our telegram bot. This helps to consolidate all the pathing and token so that
user will be able to change the directory to suit their needs without editing
the python file.

sqlCommand.py is the python files that our application used to access our database.
It consolidate all the frequently use sql query for our modules to call on providing
a more efficient way of accessing database