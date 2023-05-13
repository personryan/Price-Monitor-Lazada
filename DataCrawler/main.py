###############################################################################################
# Version No | Date of Edit   | Edited By          | Remarks                                  #
# ------------------------------------------------------------------------------------------- #
#   v 1.0    | 15 - 10 - 2021 | Ariff/Lay Kiat     | Initial file                             #
#   v 2.0    | 27 - 10 - 2021 | Bruce              | Update and combine with processing       #
#   v 2.1    | 28 - 10 - 2021 | Bruce              | Remove processing                        #
###############################################################################################

import dataPreProcessing
import configparser
config = configparser.ConfigParser()
config.read('..\\Resource\\properties.ini')
databasePath = config['DATABASE_PATH']['path']
def main():

    # Create scrape file
    print("Start Scrapping Process...")
    dataPreProcessing.scrape_URL(databasePath)
    print("------------------------------------------------------------------")

    # Clean files that were scrape
    print("Start Cleaning Process...")
    dataPreProcessing.clean_scrape_file()
    print("------------------------------------------------------------------")


if __name__ == '__main__':
    main()