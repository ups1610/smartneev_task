import os
import re
import sys
import csv
import requests
import pandas as pd
from logger import logging
from bs4 import BeautifulSoup
from exception import CustomException

class Scrap:
    def __init__(self,url) -> str:
        self.url = url

    def conn(self):
        try:
            logging.info("connecting...")

            self.response = requests.get(self.url)
            print(self.response)
            logging.info("connection successfull")

        except Exception as e:
            logging.info("error occured in connection")
            raise CustomException(e,sys)    

    def html_parser(self):
        try:
            logging.info("extracting...")
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
            logging.info("html extracted successfully")

        except Exception as e:
            logging.info("error occured in scrap")
            raise CustomException(e,sys)
        
    def scrap(self):
        try:
            data = {}
            uid = '0'
            data_size = int(self.soup.find('div', class_="tlWrp")['data-length'])
            property = self.soup.find_all('div', class_='tlWrp')[0]

            for index in range(1,data_size+1):
                search_var = "dseprojectdata tileNo_"+str(index)
                property_details = property.find('div',class_=search_var)
                url_string = property_details.find('h2',class_='tlHdng')['onclick']
                url_pattern = r'https?://[^\s]+'
                url = re.findall(url_pattern, url_string)[0]
                url = url[:-2]
                id = property_details['id'].split('_')[1]
                name = property_details.find('h2',class_='tlHdng').span.div.text.strip(' ')
                if property_details.find('div',class_='tlDscDescription'):
                   desc = property_details.find('div',class_='tlDscDescription').text.strip('\n')
                else:
                    desc = ""   
                details = {
                    'url':url,
                    'id':id,
                    'name':name,
                    'description':desc
                }
                data[uid] = details

                uid = str(int(uid) + 1)

            return data
            
        except Exception as e:
            logging.info("error occured in scrap details")    
            raise CustomException(e,sys)
    
    def data_to_excel(self,csv_file,json_data):
        try:
            frame = []
            for _,data in json_data.items():
                frame.append(data)
            # print(frame)    
            if os.path.isfile(csv_file):
                df = pd.read_csv(csv_file)
                new_df = pd.DataFrame(frame)
                df = pd.concat([df,new_df],axis=0)
            else:
                df = pd.DataFrame(frame)

            df.to_csv(csv_file,index=True)        
        except Exception as e:
            print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    # paste link here
    obj = Scrap('https://www.squareyards.com/new-projects-in-gurgaon')  
    obj.conn()
    obj.html_parser()
    data = obj.scrap()
    obj.data_to_excel('gurgaon_properties.csv',data)       