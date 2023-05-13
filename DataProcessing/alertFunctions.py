###########################################################################################
# Version No  | Date of Edit   | Edited By |      Remarks                                 #
# --------------------------------------------------------------------------------------- #
#   v 1.0     | 22 - 10 - 2021 | Ariff     | Initial file                                 #
#   v 1.1     | 24 - 10 - 2021 | Ariff     | Added getIteminfoID and getPrice function    #
#   v 1.2     | 26 - 10 - 2021 | Ariff     | Finalized functions for alert monitor        #
#   v 2.0     | 27 - 10 - 2021 | Bruce     | Update and rewrite function and remove       #
#                                          | those not needed                             #
###########################################################################################

import smtplib
import configparser
import telepot
from Resource import sqlCommand

#Fetch details from properties.ini
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
email_user = config['EMAIL']['username']
email_password = config['EMAIL']['password']
token = config['TELEGRAM']['bottoken']

def check_alert(con,itemInfoId,numPrice):
    '''check_alert: Check if there's any alert for the iteminfo w price'''
    table = "alert"
    condition = "iteminfoid = "+str(itemInfoId)+" AND "+str(numPrice)+" <= price and notify=1"
    test = sqlCommand.sql_get_specify(con,table,"alertid, userid, usertype",condition)
    return test


def send_alert(con, alertList, name, numPrice, urlid):
    '''send_alert: Send an alert to user based on usertype and change notify to 0'''
    #Declare usertype list
    emailList = []
    telegramList = []
    alertidList = []

    #Get URL
    table = "url"
    retrieve = "urllink"
    condition = "urlid = "+str(urlid)
    url = sqlCommand.sql_get_specify(con,table, retrieve, condition)[0][0]
    #Arrange userid into their usertype list
    for info in alertList:
        alertid = info[0]
        userid = info[1]
        usertype = info[2]
        alertidList.append(str(alertid))
        if usertype == "telegram":
            telegramList.append(userid)
        elif usertype == "email":
            emailList.append(userid)

    #Send alert if list is not empty
    if emailList:
        send_email(emailList, name, numPrice, url)
    if telegramList:
        send_telegram(telegramList, name, numPrice, url)

    #update notify to 0
    alertTable = "alert"
    values = "notify=0"
    alertidStr = ",".join(alertidList)
    condition = "alertid in ("+alertidStr+")"
    sqlCommand.sql_update(con, values, alertTable, condition)

def send_email(useridList, name, numPrice, url):
    '''send_email: Send alert to user via email'''

    #Set message and send to users
    subj = "Price Alert: Item Price Has Dropped!"
    message_text='Tracked Item: '+name+'\nCurrent Price:  '+str(numPrice)+'\nURL: '+url
    msg = "From: %s\nSubject: %s\n\n%s" % (email_user, subj, message_text)
    try :
        server = smtplib.SMTP("smtp.mail.yahoo.com",587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, useridList, msg)
        server.quit()
    except Exception as e:
        print ("Error sending email: "+str(e))

def send_telegram(useridList, name, numPrice, url):
    '''send_email: Send alert to user via telegram'''

    bot = telepot.Bot(token)

    #Set message and send to user
    msg = "*"+name+"* has drop to *"+str(numPrice)+"*!\nGrab it now at\n"+url

    for userid in useridList:
        try:
            bot.sendMessage(userid, msg,parse_mode='Markdown')
        except Exception as e:
            print ("Error sending message: "+str(e))
