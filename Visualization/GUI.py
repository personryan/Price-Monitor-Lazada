###########################################################################################
# Version No | Date of Edit | Edited By |  Remarks                                        #
#-----------------------------------------------------------------------------------------#
# v1.0       | 08.10.2021   | Ryan      | Intial File                                     #
# v1.1       | 11.10.2021   | Ryan      | Full Func                                       #
# v1.2       | 17.10.2021   | Ryan      | Using DB                                        #
# v1.3       | 17.10.2021   | Ryan      | Graph tile had "_"                              #
# v1.4       | 19.10.2021   | Ryan      | added user input,  (email,price)                #
# v1.5       | 24.10.2021   | Ryan      | added dropdown menu, entry for URL              #
#                                         fixed open url                                  #
# v1.6       | 24.10.2021   | Ryan      | small edits                                     #
# v1.7       | 25.10.2021   | Ryan      | edits on functions                              #
# v1.8       | 25.10.2021   | Ryan      | Become dropdownlist                             #
# v1.9       | 25.10.2021   | Ryan      | Added back searchbar                            #
# v2.0       | 27.10.2021   | Bruce     | Clean some functions, make code more efficient  #
#                                       | add check for alert, clean up labels and such   #
###########################################################################################
import re
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from textwrap import wrap
import webbrowser
from Resource import sqlCommand
import configparser

#Declare file path
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
logoPath = config['LOGO_PATH']['path']
databasePath = config['DATABASE_PATH']['path']

def replace_underscore(itemList):
    '''replace_underscore: loops list and replace underscore with space'''
    newList=[]
    for item in itemList:
        item=item.replace("_"," ")
        newList.append(item)
    return newList

def URL(iteminfoId):
    """URL: Opening URL"""
    con= sqlCommand.sql_connection(databasePath)
    urlid = sqlCommand.sql_get_specify(con, "iteminfo","urlid", "iteminfoid = " + str(iteminfoId))[0][0]
    url = sqlCommand.sql_get_specify(con, "url", "urllink", "urlid = " + str(urlid))[0][0]
    webbrowser.open(url)

def displayGraph(text):
    '''Use to display graph for items'''
    def inputData(itemInfoId):
        #get user input price and email
        price = userPrice.get()
        userid = userEmail.get()

        #price check
        try:
            float(price)
            # email check
            if re.match(r"[^@]+@[^@]+\.[^@]+", userid):
                con = sqlCommand.sql_connection(databasePath)
                usertype = "email"
                condition = "iteminfoid = "+str(itemInfoId)+" AND userid = \""+userid+"\" AND usertype='email'"
                # check if alert exist for user, if yes, update price, set notify to 1
                alertid = sqlCommand.sql_get_id(con,"alert",condition)
                if alertid != -1:
                    # update instead if exist
                    sqlCommand.sql_update(con,"price="+str(price)+", notify=1","alert","alertid = "+str(alertid))
                else:
                    # insert into database the price and email.
                    sqlCommand.sql_insert_bulk(con, [(itemInfoId, price, userid, usertype, "1")], 'alert')


                tk.messagebox.showinfo("Successful!", "Successfully added desired price and email")
                con.close()
            else:
                tk.messagebox.showinfo("Unsuccessful!", "Please enter a valid email")
        except:
            tk.messagebox.showinfo("Unsuccessful!", "Please enter a valid price")

    new= tk.Toplevel(root)
    new.transient(root)
    newCanvas = tk.Canvas(new, width=600, height=500)
    newCanvas.grid(columnspan=5, rowspan=7)
    # logo
    logo = Image.open(logoPath)
    logo = ImageTk.PhotoImage(logo)
    logoLabel = tk.Label(new,image=logo)
    logoLabel.image = logo
    logoLabel.grid(columnspan=3, column=1, row=0)

    con= sqlCommand.sql_connection(databasePath)
    itemName = text.replace(" ", "_")
    # get itemId
    itemInfoId = sqlCommand.sql_get_id(con, "iteminfo", " itemname='" + itemName + "'")

    # get logs for items
    logs = sqlCommand.sql_get_specify(con, "logs", "price,datetime", "date('now','-3 months')< datetime AND iteminfoid =" + str(itemInfoId))
    con.close()

    # put logs into list
    plots = list(logs)

    #my x and y axis
    price = [i[0] for i in plots]
    datetime = [i[1] for i in plots]

    dateList=[]
    for date in datetime:
        date=date[0:10]
        dateList.append(date)
    currentPrice= price[-1]

    #Clean title text
    text=text.replace("_"," ")
    text=' '.join(text.split())

    #Displaying graph
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax = figure.add_subplot(111)
    ax.plot(dateList,price)
    # Setting intervals of every 10 days when data has more than 7 days.
    if len(dateList)>7:
        ax.set_xticks(dateList[::10])
        ax.set_xticklabels(dateList[::10], rotation=25)

    ax.set_ylabel("Price")
    chart_type = FigureCanvasTkAgg(figure, new)
    chart_type.get_tk_widget().grid(columnspan=5,row=1)
    title = ax.set_title("\n".join(wrap(text,75)), fontsize= 10)
    title.set_y(1.05)

    #Declare labels
    currentPriceLabel = tk.Label(new, text="Current Price:",height=1,width=20, padx=15, pady=15, font="Times 11 bold")
    currentPriceLabel.grid(columnspan=3, column=0, row=3)

    desiredPriceLabel = tk.Label(new, text="Enter your desired price:",height=1,width=20, padx=15, pady=15, font="Times 11 bold")
    desiredPriceLabel.grid(columnspan=3, column=0, row=4)

    emailLabel = tk.Label(new, text="Enter your email:",height=1,width=20, padx=15, pady=15, font="Times 11 bold")
    emailLabel.grid(columnspan=3, column=0, row=5)

    #Declare input box and current price
    currentPriceText = tk.Label(new, text=str(currentPrice),height=1,width=20, padx=15, pady=15, font="Times 11 bold")
    currentPriceText.grid(columnspan=3, column=2, row=3)

    userPrice = tk.StringVar()
    desiredPriceEntry = tk.Entry(new, textvariable=userPrice, width=35)
    desiredPriceEntry.grid(columnspan=3, column=2, row=4)

    userEmail=tk.StringVar()
    emailEntry = tk.Entry(new, textvariable=userEmail,width=35)
    emailEntry.grid(columnspan=3, column=2, row=5)

    # Input into database email & desired price
    inputBtnTxt = tk.StringVar()
    inputBtn = tk.Button(new, textvariable=inputBtnTxt, command=lambda: inputData(itemInfoId), bg="#22249c", fg="white", height=4,width=6)
    inputBtnTxt.set("send")
    inputBtn.grid(columnspan=3, column=4, row=4, rowspan=2)

    #button to go to lazada webpage
    URLbtnTxt = tk.StringVar()
    URLbtn = tk.Button(new, textvariable=URLbtnTxt, command=lambda: URL(itemInfoId), bg="#f0750a", fg="white", height=1, width=10)
    URLbtnTxt.set("URL Link")
    URLbtn.grid(columnspan=3, column=1, row=6)

def openItemInfo(text):
    def search(itemChosen):
        """Comparing if catId value is given or an item is given """
        text = itemChosen
        text = text.replace(" ", "_")

        # specific item chosen, display different page
        displayGraph(text)
        itemsDropdown.destroy()

    """Extract relevant info from iteminfo table from SQL"""
    # dictionary of itemname and URL
    con = sqlCommand.sql_connection(databasePath)
    # key: itemname, value: categoryid
    itemList = []
    dctCat = dict((key, value) for key, value in sqlCommand.sql_get_all(con, "category"))
    # checking if any categories is searched, yes: shows items in the category e.g Smartphones
    if text in dctCat.values():
        #getting categoryID
        for key in dctCat:
            if dctCat[key] == text:
                #find all same categoryID items
                condition = "categoryid=" + str(key)
                #get the list of same category ID
                itemTuples = sqlCommand.sql_get_specify(con, "iteminfo", "itemname", condition)
                listOfList = [list(ele) for ele in itemTuples]
                itemList = [item for sublist in listOfList for item in sublist]
                itemList = replace_underscore(itemList)

    # Drop down for items
    itemChosen = tk.StringVar()
    itemChosen.set("Items Available")
    itemsDropdown = tk.OptionMenu(root, itemChosen, *itemList, command=search)
    itemsDropdown.configure(bg="#22249c",fg="white")
    itemsDropdown.grid(columnspan=3, column=0, row=4)
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

def enter_url():
    '''enter_url: Use to insert custom url into database for scrapping'''
    urllink = userURL.get()
    if "lazada.sg" in urllink:
        if "http://" not in urllink and "https://" not in urllink:
            urllink = "https://"+urllink
        url_exist = add_url_to_db(urllink)
        if url_exist == 1:
            title = "Unsuccessful!"
            text = "URL already exist in our system, try finding the item first!"
        else:
            title = "Successful!"
            text = "Successfully added URL"
    else:
        title = "Unsuccessful!"
        text = "Please enter a valid Lazada link or add https:// to your link"
    tk.messagebox.showinfo(title, text)

def itemFind():
    def openItemFind(itemList):
        def search(itemChosen):
            """Displaying chosen item's graph etc. """
            text = itemChosen
            text = text.replace(" ", "_")
            displayGraph(text)
            itemsDropdown.destroy()

        itemList = replace_underscore(itemList)
        # Drop down for items
        itemChosen = tk.StringVar()
        itemChosen.set("Items Available")
        itemsDropdown = tk.OptionMenu(root, itemChosen, *itemList, command=search)
        itemsDropdown.configure(bg="#22249c", fg="white")
        itemsDropdown.grid(columnspan=3, column=0, row=4)

    """Comparing if catId value is given or an item is given """
    text=searched.get()
    #connect database and get iteminfo related to search
    con = sqlCommand.sql_connection(databasePath)
    relatedItems = sqlCommand.sql_get_specify(con, "iteminfo", "itemname", " LOWER(itemname) like '%" + text.lower().replace(" ","_") + "%'")
    con.close()
    relatedItems = list_tuple_to_list(relatedItems)

    #to display items= eg.apple show all apple products
    if relatedItems:
        openItemFind(relatedItems)
    else:
        tk.messagebox.showinfo("Unsuccesful!","Item searched not found!\n\nYou can do the following:\n\n1.Use the categories dropdown link to browse for items\n2.Search using your own product link")

def list_tuple_to_list(tuple):
    '''list_tuple_to_list:Convert list of tuple to list'''
    listOfList = [list(ele) for ele in tuple]
    return [item for sublist in listOfList for item in sublist]

#Initialze canvas
root = tk.Tk()
root.wm_title("Price Monitor")
root.resizable(False, False)
canvas = tk.Canvas(root, width=600, height=300)
canvas.grid(columnspan=5, rowspan=6)

#Initialize Logo
logo = Image.open(logoPath)
logo = ImageTk.PhotoImage(logo)
logoLabel = tk.Label(image=logo)
logoLabel.image = logo
logoLabel.grid(columnspan=3,column=0,row=0)

#Instructions
instructions = tk.Label(root, text="Search for an item or look at available categories")
instructions.grid(columnspan=3, column=0, row=1)

#Search box and button
searched= tk.StringVar()
searchBox= tk.Entry(root, textvariable=searched, width= 20)
searchBox.grid(columnspan=3,column=0,row=2)
searchBtnTxt=tk.StringVar()
searchBtn= tk.Button(root, textvariable=searchBtnTxt, command= lambda:itemFind(),bg="#22249c",fg="white",height=1, width=6)
searchBtnTxt.set("search")
searchBtn.grid(columnspan=4, column=1, row=2)

#Drop down for categories
con = sqlCommand.sql_connection(databasePath)
categories= sqlCommand.sql_get_specify(con, "category", "categoryname")
con.close()
options = list_tuple_to_list(categories)
clicked= tk.StringVar()
clicked.set("Categories")
categoriesDropdown= tk.OptionMenu(root,clicked, *options, command=openItemInfo)
categoriesDropdown.configure(bg="#22249c",fg="white")
categoriesDropdown.grid(columnspan=3, column=0, row=3)

#instructions for new link
instructionsURL = tk.Label(root, text="Can't find your item? Add your own lazada link!")
instructionsURL.grid(columnspan=3, column=0, row=5)

#Entering new link
userURL= tk.StringVar()
userURLbox= tk.Entry(root, textvariable=userURL, width= 60)
userURLbox.grid(columnspan=3,column=0,row=6)
userURLbtnTxt=tk.StringVar()
userURLbtn= tk.Button(root, textvariable=userURLbtnTxt, command= lambda:enter_url(),bg="#f0750a",fg="white",height=1, width=6)
userURLbtnTxt.set("enter")
userURLbtn.grid(columnspan=3, column=0, row=7)

#instructions for new link
note = tk.Label(root, text="Please note: Items will only be added on next scrape")
note.grid(columnspan=3, column=0, row=8)

canvas = tk.Canvas(root, width=600, height=250)
canvas.grid(columnspan=3)
root.mainloop()