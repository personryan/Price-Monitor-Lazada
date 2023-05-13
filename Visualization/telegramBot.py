########################################################################################
# Version No | Date of Edit | Edited By |  Remarks                                     #
# ------------------------------------------------------------------------------------ #
# v1.0       | 21.10.2021   | LK        |  Intial File                                 #
# v1.1       | 21.10.2021   | LK        |  Testing out Category/Brand as button        #
# v1.2       | 24.10.2021   | LK        |  Adding option for user to add url           #
# v1.3       | 24.10.2021   | LK        |  Changed from showing url to price range     #
# v1.4       | 24.10.2021   | LK        |  Small edits for grammar                     #
# v1.5       | 24.10.2021   | Bruce     |  Add backtrack, and shows item info as msg   #
# v1.6       | 24.10.2021   | Bruce     |  Add price alert function base foundation    #
# v1.7       | 27.10.2021   | LK        |  Work upon price alert foundation, now able  #
#            |              |           |  to update alert and notify on db            #
# v1.8       | 27.10.2021   | LK        |  Changed price adding to tag to item and user#
# v1.9       | 28.10.2021   | LK        |  Tidy up code                                #
# v2.0       | 28.10.2021   | Bruce     |  Make code more efficient, added search      #
########################################################################################

import sys
import time
import telepot
from Resource import sqlCommand
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import configparser

#Fetch details from properties.ini
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
token = config['TELEGRAM']['bottoken']
databasePath = config['DATABASE_PATH']['path']

def database_search_specific(table, column, condition=""):
    """database_search_specific: To get a list of items from based on the inputs."""
    con = sqlCommand.sql_connection(databasePath)
    tuples = sqlCommand.sql_get_specify(con, table, column, condition)
    list_of_list = [list(ele) for ele in tuples]
    flatten_list = [item for sublist in list_of_list for item in sublist]
    con.close()
    return flatten_list

def database_get_id(table, condition):
    '''database_get_id: get the id of a table based on condition, return id'''
    con = sqlCommand.sql_connection(databasePath)
    id = sqlCommand.sql_get_id(con, table, condition)
    con.close()
    return id

def database_update_alert(value,condition):
    '''database_update_alert: update alert w proper notify'''
    con = sqlCommand.sql_connection(databasePath)
    sqlCommand.sql_update(con, value, "alert", condition)
    con.close()

def add_url_to_db(url_input):
    '''add_url_to_db: Function to add url to database by first checking if exists within the database. If link does not exist,
    it will be added to the db'''
    con = sqlCommand.sql_connection(databasePath)
    table = "url"
    url_id = sqlCommand.sql_get_id(con, table, "urllink = '"+str(url_input)+"'")
    exist = 0
    if url_id == -1:
        sqlCommand.sql_insert_one(con, "'"+str(url_input)+"', 0", table)
    else:
        exist = 1
    con.close()
    return exist

def search_by_item_through_(condition):
    '''search_by_item_through_: Search items through selected category or brand'''
    item_info = database_search_specific("iteminfo", "itemname", condition)
    item_id = database_search_specific("iteminfo", "iteminfoid", condition)
    item_info = [w.replace("_", " ") for w in item_info]
    keyboard_input = [[InlineKeyboardButton(text=str(item_info[i]), callback_data="itemid: " + str(item_id[i]))]
                      for i in range(0, len(item_info))]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_input)
    return keyboard

def search_by_category():
    '''search_by_category: Search database using category and returns the search through keyboard markup'''
    category = database_search_specific("category", "categoryname")
    keyboard_input = [[KeyboardButton(text="Category: " + str(category[item]))] for item in range(0, len(category))]
    keyboard_input.append([KeyboardButton(text="/Home")])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_input)
    return keyboard

def search_by_brand():
    '''search_by_brand: Search database using brand and returns the search through keyboard markup'''
    brand = database_search_specific("brand", "brandname")
    keyboard_input = [[KeyboardButton(text="Brand: " + str(brand[item]))] for item in range(0, len(brand))]
    keyboard_input.append([KeyboardButton(text="/Home")])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_input)
    return keyboard

def get_alert_id(item_info, user_id):
    '''get_alert_id: Returns alert_id by checking db if has this alert_id'''
    condition = "iteminfoid="+str(item_info)+" AND notify=1 AND userid="+str(user_id)
    con = sqlCommand.sql_connection(databasePath)
    alert_id = sqlCommand.sql_get_id(con, "alert", condition)
    con.close()
    return alert_id

def check_notify(item_info_id, user_id):
    '''check_notify: Checks the database for the value of notify in the alert table'''
    condition = "iteminfoid=" + str(item_info_id) + " AND userid=" + str(user_id)
    notify = database_search_specific("alert", "notify", condition)
    return notify

def command_received(userID, textReceived):
    '''command_received: When the bot received a /msg, reply format'''
    textReceived = textReceived.lower()
    reply_markup=""
    if textReceived == "/help":
        text_input = "To start using the bot, type /start!\nSearch via category: /category\nSearch via brand: /brand\nOr do your own search by typing\nSearch: apple\nTo search for items with apple in it"
    elif "/start" == textReceived or "/home" == textReceived:
        text_input = "Hello, welcome to our Price Monitor App! To start you can choose the following button or search for your own items via 'Search: <item>'\n\nIf you need more assistant: /help"
        reply_markup=ReplyKeyboardMarkup(keyboard=[
                             [KeyboardButton(text="/Add URL"), KeyboardButton(text="/Catalog")]])
    elif textReceived == "/add url":
        text_input = "Please enter URL link: "
    elif textReceived == "/catalog":
        text_input = "Please choose what to view"
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/Category"),
                                                    KeyboardButton(text="/Brand"),KeyboardButton(text="/Home")]])
    elif textReceived == "/category":
        text_input = "Choose a category"
        reply_markup = search_by_category()
    elif textReceived == "/brand":
        text_input = "Choose a brand"
        reply_markup = search_by_brand()
    else:
        text_input = "Command not recognized, please refer to /help"
    bot.sendMessage(userID, text_input, reply_markup=reply_markup,parse_mode='Markdown')


def on_chat_message(msg):
    '''on_chat_message: What to do when text received'''
    userId = msg['chat']['id']
    textReceived = msg['text']
    if '/' in textReceived[0]:  # On command received
        command_received(userId, textReceived)

    elif "Category: " in textReceived:  # Searches with category
        category_name = textReceived.replace("Category: ", "")
        condition = "categoryname=\"" + category_name + "\""
        category_id = database_get_id("category",condition)
        searchCondition = "categoryid ="+str(category_id)
        reply_markup = search_by_item_through_(searchCondition)
        bot.sendMessage(userId, textReceived, reply_markup=reply_markup)

    elif "Brand: " in textReceived:  # Searches with brand
        brand_name = textReceived.replace("Brand: ", "")
        condition = "brandname=\"" + brand_name + "\""
        brand_id = database_get_id("brand", condition)
        searchCondition = "brandId ="+str(brand_id)
        reply_markup = search_by_item_through_(searchCondition)
        bot.sendMessage(userId, textReceived, reply_markup=reply_markup)

    elif "search:" in textReceived.lower(): #User search
        textSearch = textReceived.lower().split("search:")[1]
        textSearch = textSearch.strip()
        textSearch = textSearch.replace(" ","_")
        searchCondition = "itemname like \"%"+textSearch+"%\""
        reply_markup = search_by_item_through_(searchCondition)
        bot.sendMessage(userId, textReceived, reply_markup=reply_markup)

    elif "lazada.sg" in textReceived: #URL received
        if "http://" not in textReceived and "https://" not in textReceived:
            textReceived = "https://"+textReceived
        url_exist = add_url_to_db(textReceived)
        if url_exist == 1:
            textToSent = "Failed to add product URL, this product already exist in our system!"
        else:
            textToSent = "URL successfully added! Item will only be shown on next scrape"
        bot.sendMessage(userId, textToSent)

    else: #Other messages
        bot.sendMessage(userId, "Please use /start or /help")


def on_callback_query(msg):
    '''on_callback_query: When user click on items'''
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    # For item selected, query sql table for it and return URL
    if "itemid: " in query_data:
        item_info_id = query_data.replace("itemid: ", "")
        condition = "iteminfoid="+str(item_info_id)
        curr_price_condition = condition+" ORDER BY logsid desc LIMIT 1"

        #Get the pricing
        item_min_price = round(database_search_specific("logs", "min(price)", condition)[0],2)
        item_max_price = round(database_search_specific("logs", "max(price)", condition)[0],2)
        item_curr_price = round(database_search_specific("logs", "price", curr_price_condition)[0],2)

        #Set text
        item_name_text = "Item: " + str(database_search_specific("iteminfo", "itemname", condition)[0])
        item_name_text = item_name_text.replace("_", " ")
        item_price_range_text = "Price of item varies from: $" + str(item_min_price) + " - $" + str(item_max_price)
        current_price_text = "Current price: " + str(item_curr_price)

        urlid = database_search_specific("iteminfo", "urlid", condition)
        link = database_search_specific("url", "urllink", "urlid ="+str(urlid[0]))

        ten_percent_drop = str(round(float(item_curr_price) * 0.90, 2))
        five_percent_drop = str(round(float(item_curr_price) * 0.95, 2))
        price_drop = str(round(float(item_curr_price) - 0.01, 2))

        alert_id = get_alert_id(item_info_id, from_id)  # get any existing alert for users and items

        #set callback for the prices
        notify_callback1 = "addalert;iteminfoid=" + str(item_info_id) + ";price=" + str(price_drop) + ";userid=" + str(
            from_id)+";notify=1"
        notify_callback2 = "addalert;iteminfoid=" + str(item_info_id) + ";price=" + str(five_percent_drop) + ";userid=" + str(
            from_id)+";notify=1"
        notify_callback3 = "addalert;iteminfoid=" + str(item_info_id) + ";price=" + str(ten_percent_drop) + ";userid=" + str(
            from_id)+";notify=1"
        remove_notify = "removenotify;iteminfoid=" + str(item_info_id) + ";userid=" + str(from_id)+";alertid="+str(alert_id)

        keyboard_input = [
            [InlineKeyboardButton(text=f"Notify me when price drop below current price!",
                                  callback_data=notify_callback1)],
            [InlineKeyboardButton(text=f"Notify me when price drop below 95% | {five_percent_drop}",
                                  callback_data=notify_callback2)],
            [InlineKeyboardButton(text=f"Notify me when price drop below 90% | {ten_percent_drop}",
                                  callback_data=notify_callback3)]]

        if not alert_id == -1:  # Check for existing alert ID
             keyboard_input.append([InlineKeyboardButton(text=f"Disable current notification",callback_data=remove_notify)])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_input)
        bot.sendMessage(from_id, item_name_text + "\n" + item_price_range_text + "\n" + current_price_text + "\n" + link[0],
                            reply_markup=keyboard)

    elif "addalert;" in query_data:
        raw1 = str(query_data)
        data = raw1.split(";")
        item_info_id = str(data[1]).replace("iteminfoid=", "")
        alert_price = str(data[2]).replace("price=", "")
        user_id = str(data[3]).replace("userid=", "")
        notify = str(data[4]).replace("notify=", "")
        notify_id = check_notify(item_info_id, user_id)

        if not notify_id:  # If no alert for items
            usertype = "telegram"
            con = sqlCommand.sql_connection(databasePath)
            sqlCommand.sql_insert_bulk(con, [(item_info_id, alert_price, user_id, usertype, notify)], "alert")
            con.close()
            bot.sendMessage(user_id, text="Alert created.", reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                             [KeyboardButton(text="/Home")]]))
        else:
            value = "price="+alert_price + ", notify="+notify
            condition = "iteminfoid=" + str(item_info_id) + " AND userid=" + str(user_id)
            database_update_alert(value, condition)
            bot.sendMessage(user_id, text="Alert has been updated.", reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="/Home")]]))
    elif "removenotify" in query_data:
        raw1 = str(query_data)
        data = raw1.split(";")
        user_id = str(data[2]).replace("userid=", "")
        alert_id = str(data[3]).replace("alertid=", "")
        condition = "alertid="+str(alert_id)
        value = "notify=0"
        database_update_alert(value, condition)
        bot.sendMessage(user_id, text="Alert for item has been disabled", reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="/Home")]]))
    else:
        print("query" + str(query_data))

def main():
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()
    print('Bot started to listen.')
    while 1:
        time.sleep(100)

bot = telepot.Bot(token)

if __name__ == '__main__':
    main()
