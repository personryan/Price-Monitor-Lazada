###########################################################################################################
# Version No | Date of Edit | Edited By | Remarks                                                         #
#---------------------------------------------------------------------------------------------------------#
#   v 1.0    |  14-10-2021  |  Bruce W  | Initial File // INTERNAL USE ONLY                               #
#   v 1.1    |  22-10-2021  |  Bruce W  | Added url table                                                 #
###########################################################################################################

import sqlite3
from Resource import sqlCommand
import configparser
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
databasePath = config['DATABASE_PATH']['path']

def sql_create_table(con):
    '''sql_create_table: Use to create the database table FIRST TIME USE ONLY!!'''
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE category(categoryid INTEGER PRIMARY KEY, categoryname TEXT)")
    cursorObj.execute("CREATE TABLE seller(sellerid INTEGER PRIMARY KEY, sellername TEXT)")
    cursorObj.execute("CREATE TABLE brand(brandid INTEGER PRIMARY KEY, brandname TEXT)")
    cursorObj.execute("CREATE TABLE url(urlid INTEGER PRIMARY KEY, urllink TEXT, valid INTEGER DEFAULT 0)")
    cursorObj.execute("CREATE TABLE iteminfo(iteminfoid INTEGER PRIMARY KEY, itemname TEXT, urlid INTEGER, categoryid INTEGER, sellerid INTEGER, brandid INTEGER,"
                      " FOREIGN KEY(urlid) REFERENCES url(urlid), FOREIGN KEY(categoryid) REFERENCES category(categoryid),"
                      " FOREIGN KEY(sellerid) REFERENCES seller(sellerid), FOREIGN KEY(brandid) REFERENCES brand(brandid))")
    cursorObj.execute("CREATE TABLE logs(logsid INTEGER PRIMARY KEY, price REAL, rating REAL, iteminfoid INTEGER, datetime NUMERIC, FOREIGN KEY(iteminfoid) REFERENCES iteminfo(iteminfoid))")
    cursorObj.execute("CREATE TABLE alert(alertid INTEGER PRIMARY KEY, iteminfoid INTEGER, price REAL, userid TEXT, usertype TEXT, notify INTEGER, FOREIGN KEY(iteminfoid) REFERENCES iteminfo(iteminfoid))")
    con.commit()

def sql_delete_table(con):
    '''sql_delete_table: Delete all tables'''
    cursorObj = con.cursor()
    cursorObj.execute("DROP TABLE IF EXISTS category")
    cursorObj.execute("DROP TABLE IF EXISTS seller")
    cursorObj.execute("DROP TABLE IF EXISTS brand")
    cursorObj.execute("DROP TABLE IF EXISTS url")
    cursorObj.execute("DROP TABLE IF EXISTS iteminfo")
    cursorObj.execute("DROP TABLE IF EXISTS logs")
    cursorObj.execute("DROP TABLE IF EXISTS alert")
    con.commit()


#con = sqlite3.connect(databasePath)
# list = sqlCommand.sql_get_specify(con,"url","urllink")
# dataAdd = []
# for row in list:
#     #print(row)
#     url = row[0]
#     dataAdd.append([url,0])

#sql_delete_table(con)
#sql_create_table(con)
#sqlCommand.sql_insert_bulk(con,dataAdd,"url")
#con.close()

