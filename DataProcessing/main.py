###############################################################################################
# Version No | Date of Edit   | Edited By          | Remarks                                  #
# ------------------------------------------------------------------------------------------- #
#   v 1.0    | 17 - 10 - 2021 | Bruce              | Initial file                             #
###############################################################################################

import dataProcesser
import configparser

#Fetch details from properties.ini
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
databasePath = config['DATABASE_PATH']['path']
def main():

    # Process files that were clean
    print("Start Processing Process...")
    dataProcesser.process_file(databasePath)
    print("------------------------------------------------------------------")

if __name__ == '__main__':
    main()