###########################################################################################################
# Version No | Date of Edit | Edited By | Remarks                                                         #
#---------------------------------------------------------------------------------------------------------#
#   v 1.0    |  12-10-2021  |  Bruce W  | Initial File                                                    #
#   v 1.1    |  12-10-2021  |  Bruce W  | Added alert table                                               #
#   v 1.2    |  12-10-2021  |  Bruce W  | Added get table values for alert table                          #
#   v 1.3    |  14-10-2021  |  Bruce W  | Added create table for brand, foreign key in iteminfo and       #
#            |              |           | get table values                                                #
#   v 1.4    |  16-10-2021  |  Bruce W  | update sql_get_id, adds sql_get_specify                         #
#   v 1.5    |  22-10-2021  |  Bruce W  | add new table urlinfo, update iteminfo, update rating to real   #
#   v 1.6    |  24-10-2021  |  Bruce W  | add notify in alert table                                       #
###########################################################################################################

import sqlite3
from sqlite3 import Error

def sql_connection(db_name):
    '''sql_connection: establish connection to the database'''
    try:
        con = sqlite3.connect(db_name)
        return con
    except Error:
        print(Error)

def sql_create_table(con):
    '''sql_create_table: Use to create the database table FIRST TIME USE ONLY!!'''
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE category(categoryid INTEGER PRIMARY KEY, categoryname TEXT)")
    cursorObj.execute("CREATE TABLE seller(sellerid INTEGER PRIMARY KEY, sellername TEXT)")
    cursorObj.execute("CREATE TABLE brand(brandid INTEGER PRIMARY KEY, brandname TEXT)")
    cursorObj.execute("CREATE TABLE url(urlid INTEGER PRIMARY KEY, urllink TEXT, valid INTEGER)")
    cursorObj.execute("CREATE TABLE iteminfo(iteminfoid INTEGER PRIMARY KEY, itemname TEXT, urlid INTEGER, categoryid INTEGER, sellerid INTEGER, brandid INTEGER,"
                      " FOREIGN KEY(urlid) REFERENCES url(urlid), FOREIGN KEY(categoryid) REFERENCES category(categoryid),"
                      " FOREIGN KEY(sellerid) REFERENCES seller(sellerid), FOREIGN KEY(brandid) REFERENCES brand(brandid))")
    cursorObj.execute("CREATE TABLE logs(logsid INTEGER PRIMARY KEY, price REAL, rating REAL, iteminfoid INTEGER, datetime NUMERIC,"
                      " FOREIGN KEY(iteminfoid) REFERENCES iteminfo(iteminfoid))")
    cursorObj.execute("CREATE TABLE alert(alertid INTEGER PRIMARY KEY, iteminfoid INTEGER, price REAL, userid TEXT, usertype TEXT, notify INTEGER DEFAULT 1,"
                      " FOREIGN KEY(iteminfoid) REFERENCES iteminfo(iteminfoid))")
    con.commit()

def sql_insert_one(con, values, table):
    '''sql_insert_one: Insert one data into TABLE w VALUES, return ID'''
    cursorObj = con.cursor()
    cursorObj.execute("INSERT INTO " + table + "("+get_table_values(table)+") VALUES (" + values + ")")
    con.commit()
    return cursorObj.lastrowid

def sql_insert_bulk(con,data,table):
    '''sql_insert_bulk: Insert bulk data into TABLE w VALUES'''
    cursorObj = con.cursor()
    cursorObj.executemany("INSERT INTO " + table + "("+get_table_values(table)+") VALUES("+get_table_values_placeholder(table)+")", data)
    print()
    con.commit()

def sql_update(con, values, table, condition):
    '''sql_update: update table'''
    cursorObj = con.cursor()
    cursorObj.execute("UPDATE "+ table + " SET " + values + " WHERE " + condition)
    con.commit()

def sql_get_all(con, table, condition=""):
    '''sql_get_all: Select whatever(default all) from TABLE w condition if any; return a list'''
    cursorObj = con.cursor()
    if(condition==""):
        cursorObj.execute("SELECT * FROM " + table)
    else:
        cursorObj.execute("SELECT * FROM " + table + " WHERE " + condition)
    return cursorObj.fetchall()

def sql_get_specify(con, table, retrieve, condition=""):
    '''sql_get_specify: Select specify from TABLE w condition if any; return a list'''
    cursorObj = con.cursor()
    if(condition==""):
        cursorObj.execute("SELECT " + retrieve + " FROM " + table)
    else:
        cursorObj.execute("SELECT " + retrieve + " FROM " + table + " WHERE " + condition)
    return cursorObj.fetchall()

def sql_get_id(con, table, condition):
    '''sql_get_id: Select ID from TABLE w condition if any; return one ID'''
    cursorObj = con.cursor()
    cursorObj.execute("SELECT "+ get_table_id(table) +" FROM " + table + " WHERE " + condition)
    tuple = cursorObj.fetchone()
    if tuple == None:
        return -1
    else:
        return tuple[0]

def get_table_values_placeholder(table):
    '''get_table_values_placeholder: Get the placeholder for bulk insert'''
    categoryvalues=sellervalues=brandvalues="?"
    alertvalue=iteminfovalues="?, ?, ?, ?, ?"
    urlvalues="?, ?"
    logsvalues="?, ?, ?, ?"

    if(table=="category"):
        return categoryvalues
    elif(table=="seller"):
        return sellervalues
    elif(table=="brand"):
        return brandvalues
    elif(table=="iteminfo"):
        return iteminfovalues
    elif(table=="logs"):
        return logsvalues
    elif(table=="alert"):
        return alertvalue
    elif(table=="url"):
        return urlvalues

def get_table_values(table):
    '''get_table_values: Get the table values'''
    categoryvalues="categoryname"
    sellervalues="sellername"
    brandvalues="brandname"
    urlvalues="urllink, valid"
    iteminfovalues="itemname, urlid, categoryid, sellerid, brandid"
    logsvalues="price, rating, iteminfoid, datetime"
    alertvalue="iteminfoid, price, userid, usertype, notify"

    if(table=="category"):
        return categoryvalues
    elif(table=="seller"):
        return sellervalues
    elif(table=="brand"):
        return brandvalues
    elif(table=="iteminfo"):
        return iteminfovalues
    elif(table=="logs"):
        return logsvalues
    elif(table=="alert"):
        return alertvalue
    elif(table=="url"):
        return urlvalues

def get_table_id(table):
    '''get_table_id: Get the table id'''
    return table+"id"