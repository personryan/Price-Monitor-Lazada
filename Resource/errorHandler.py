###########################################################################################################
# Version No | Date of Edit | Edited By | Remarks                                                         #
#---------------------------------------------------------------------------------------------------------#
#   v 1.0    |  28-10-2021  |  Bruce W  | Initial File                                                    #
###########################################################################################################

import configparser
from datetime import datetime
import os

config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
crashLogsPath = config['CRASH_LOGS']['logfile']
errorPath = config['CRASH_LOGS']['errordatapath']

def writeLogs(strInput):
    '''writeLogs: Open path to write logs, if file doesn't exist, will create file'''
    print("Error Face! Please check "+crashLogsPath+" for more information!")
    try:
        file = open(crashLogsPath, 'a+', encoding='utf-8')
        file.write(str(datetime.now()) + "|"+strInput + "\n")
        file.close()
    except Exception as e:
        writeLogs(str(datetime.now()) + "|Error Message: "+str(e)+"\n")

def moveErrorFile(filename):
    '''moveErrorFile: move error file to directory for investigation'''
    try:
        rawFilename = os.path.basename(filename)
        os.rename(filename,errorPath+rawFilename)
        print(str(filename)+" has been moved into "+str(errorPath))
    except Exception as e:
        writeLogs(str(e))
