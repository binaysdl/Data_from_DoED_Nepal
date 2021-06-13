import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np


def get_title(soup):
    # Stripping white spaces and enter from title
    title = " ".join(str(soup.html.head.title.string).split())
    title = title.replace(" ", "_")
    title = title.replace(":", "_")
    title = title.replace("__", "_")
    title = title.replace("__", "_")
    return title

def get_rows(table):
    rows = table.find_all('tr')
    rows_list=list()
    for tr in rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        rows_list.append(row)
    rows_list = rows_list[1:]
    return rows_list

def get_headers(table,rows_list):
    headers = table.find_all('tr')
    headers_list = list()
    for th in headers:
        th_ = th.find_all('th')
        header = [i.text for i in th_]
        headers_list.append(header)
    headers_list = headers_list[:1]
    data_size = np.shape(rows_list)
    # These are double bracket arrays; Now, obtaining single numpy array of header
    headers_list = headers_list[0]
    Lat_Long_find = 0
    if len(rows_list) > 0:
        column_length = data_size[1]-1
    else:
        column_length = len(headers_list)+2
    for x in range(column_length):
        if headers_list[x] == 'Latitiude N' and Lat_Long_find == 0:
            Lat_Long_find = 1
            headers_list = np.insert(headers_list, x+1,'Latitude N I')
        if headers_list[x] == 'Longitude E' and Lat_Long_find == 1:
            Lat_Long_find = 2
            headers_list = np.insert(headers_list, x+1, "Longitude E I")
            break
    return headers_list

# Import Page and Print Contents
web_list=list()
for x in range(0,100):
    web_list.append('http://doed.gov.np/license/'+str(x))

webpage_responsive = list()
webpage_title = list()
# Extract Only Responsive Pages
for x in range(len(web_list)):
    page = requests.get(web_list[x])
    y = page.status_code
    if y >=200 and y < 300:
        webpage_responsive.append(web_list[x])
        soup = BeautifulSoup(page.content, 'html.parser')
        title = get_title(soup)
        webpage_title.append(title)
# Data of responsive pages for future use
page_info = np.vstack((webpage_title,webpage_responsive))
df_webpage_list = pd.DataFrame(page_info)
df_webpage_list=df_webpage_list.T

# Changing columns name with index number
mapping = {df_webpage_list.columns[0]: 'Page Title', df_webpage_list.columns[1]: 'Web Link'}
df_webpage_list = df_webpage_list.rename(columns=mapping)
df_webpage_list.columns.values[0] = 'Page Title'
df_webpage_list.to_csv("DoED_Data/00_Web_Page_List.csv",index = False)

for x in range(0,len(webpage_responsive)):
    print("Webpage: ", webpage_title[x])
    webpage = webpage_responsive[x]
    page = requests.get(webpage)
    soup = BeautifulSoup(page.content,'html.parser')
    title = get_title(soup)

    # Extracting Table
    table = soup.find_all("table")[0]
    rows_list = get_rows(table)
    headers_list = get_headers(table, rows_list)

    # Converting to pandas dataframe
    df = pd.DataFrame(rows_list, columns= headers_list)
    print(df.columns)
    if 'Latitiude N' in df.columns and len(rows_list)>0:
        # Splitting the decimal degrees, minutes and seconds
        df['Latitiude N'] = df['Latitiude N'].str.replace(r"[\"\',]", '', regex=True)
        df[['Lat_I_Deg', 'Lat_I_Min', 'Lat_I_Sec']] = df['Latitiude N'].str.split(' ', expand=True)
        df['Lat_I_Deg'] = df['Lat_I_Deg'].str.extract('(\d+)', expand=False).astype(int)
        df['Lat_I_Min'] = df['Lat_I_Min'].str.extract('(\d+)', expand=False).astype(int)
        df['Lat_I_Sec'] = df['Lat_I_Sec'].str.extract('(\d+)', expand=False).astype(int)

        df['Latitude N I'] = df['Latitude N I'].str.replace(r"[\"\',]", '', regex=True)
        df[['Lat_II_Deg', 'Lat_II_Min', 'Lat_II_Sec']] = df['Latitude N I'].str.split(' ', expand=True)
        df['Lat_II_Deg'] = df['Lat_II_Deg'].str.extract('(\d+)', expand=False).astype(int)
        df['Lat_II_Min'] = df['Lat_II_Min'].str.extract('(\d+)', expand=False).astype(int)
        df['Lat_II_Sec'] = df['Lat_II_Sec'].str.extract('(\d+)', expand=False).astype(int)

        df['Longitude E'] = df['Longitude E'].str.replace(r"[\"\',]", '', regex=True)
        df[['Long_I_Deg', 'Long_I_Min', 'Long_I_Sec']] = df['Longitude E'].str.split(' ', expand=True)
        df['Long_I_Deg'] = df['Long_I_Deg'].str.extract('(\d+)', expand=False).astype(int)
        df['Long_I_Min'] = df['Long_I_Min'].str.extract('(\d+)', expand=False).astype(int)
        df['Long_I_Sec'] = df['Long_I_Sec'].str.extract('(\d+)', expand=False).astype(int)

        df['Longitude E I'] = df['Longitude E I'].str.replace(r"[\"\',]", '', regex=True)
        df[['Long_II_Deg', 'Long_II_Min', 'Long_II_Sec']] = df['Longitude E I'].str.split(' ', expand=True)
        df['Long_II_Deg'] = df['Long_II_Deg'].str.extract('(\d+)', expand=False).astype(int)
        df['Long_II_Min'] = df['Long_II_Min'].str.extract('(\d+)', expand=False).astype(int)
        df['Long_II_Sec'] = df['Long_II_Sec'].str.extract('(\d+)', expand=False).astype(int)

        # Deducing the decimal degrees from the decimal degrees, minutes and seconds
        df['Latitude_N_I_dd'] = df['Lat_I_Deg'] + df['Lat_I_Min'] / 60 + df['Lat_I_Sec'] / 3600
        df['Latitude_N_II_dd'] = df['Lat_II_Deg'] + df['Lat_II_Min'] / 60 + df['Lat_II_Sec'] / 3600
        df['Longitude_E_I_dd'] = df['Long_I_Deg'] + df['Long_I_Min'] / 60 + df['Long_I_Sec'] / 3600
        df['Longitude_E_II_dd'] = df['Long_II_Deg'] + df['Long_II_Min'] / 60 + df['Long_II_Sec'] / 3600

    # Saving Files as csv
    filename = "DoED_Data/"+str(x+1)+"_" + str(title)+".csv"
    print(filename)
    df.to_csv(filename,index=False)
    # remove loop variables for next loop
    del table, webpage, title, soup, rows_list, headers_list, df