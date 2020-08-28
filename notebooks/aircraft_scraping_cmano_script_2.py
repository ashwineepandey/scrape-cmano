#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Imports" data-toc-modified-id="Imports-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Imports</a></span></li></ul></div>

# #### Imports

# In[1]:


import logging
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd
import re


# In[2]:


logging.basicConfig(level=logging.DEBUG)


# In[3]:


def _get_response(url):
    response = requests.get(url)
    return response


# In[4]:


def get_soup_object(url):
    response = _get_response(url)
    #Insert logic to check
    #if response = 200
    soup = BeautifulSoup(response.text, "html.parser")
    #else handle exceptions
    return soup


# In[5]:


def get_aircraft_urls(url, aircraft_url_input_dir):
    df_aircraft_urls = pd.read_table(aircraft_url_input_dir)
    aircraft_url_list = []
    for index in range(len(df_aircraft_urls)):
        url_suffix_aircraft = df_aircraft_urls['URL'][index]
        aircraft_url_list.append(f'{url}{url_suffix_aircraft}')
    logging.debug(f'URLs read in successfully.')
    return df_aircraft_urls, aircraft_url_list


# In[6]:


def _read_table(table_number, soup):
    table = soup.find_all('table')[table_number]
    rows = table.find_all('tr')
    row_list = list()
    for tr in rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        row_list.append(row)
    flat_list = [item for sublist in row_list for item in sublist]
    return flat_list


# In[7]:


def _get_table_header(table, index_list, header_list):
    
    for i in range(len(table)):
        header = table[i].find_all('th')
        header_string = [i.text for i in header]
        index_list.append(i)
        header_list.append(header_string)
        logging.debug(f"Index: {i}")
        logging.debug(f"Header: {header_string}")
    
    return index_list, header_list


# In[8]:


def count_tables_on_page(soup):
    table = soup.find_all('table')
    number_of_tables = len(table)
    logging.debug(f"There are {number_of_tables} tables on this page.")
    index_list = []
    header_list = []
    if len(table) > 0:
        index_list, header_list = _get_table_header(table, index_list, header_list)
    else:
        logging.error(f"No tables found.")
    
    table_header_dict = {"index": index_list,
            "header": header_list}
    
    return number_of_tables, table_header_dict


# In[9]:


def read_table_one(soup, table_number):
    
    flat_list = _read_table(table_number, soup)
    
    logging.debug(f"flat_list is {flat_list}")
    
    _list = []
    dict_keys = []
    dict_values = []
    
    flat_list = flat_list[:13] #Specific - change them ???????????
    
    for i in range(len(flat_list)):
        _list_val = flat_list[i]
        _sublist = _list_val.split(': ') #Specific to this context
        _list.append(_sublist)
    
    logging.debug(f"_list: {_list}")
    logging.debug(f"length of _list: {len(_list)}")
    
    for j in range(len(_list)):
        logging.debug(f"Current dict key is: {_list[j][0]}.")
        dict_keys.append(_list[i][0])
        logging.debug(f"Current dict value is: {_list[j][1]}.")
        dict_values.append(_list[i][1])
    
    _dict = dict(zip(dict_keys, dict_values))
    
    df_table_1 = pd.DataFrame().append(_dict, ignore_index=True)
    
    return df_table_1


# In[10]:


def check_pattern_existence(pattern, string):
    if re.search(pattern, string):
        indicator = True
    else:
        indicator = False
    
    return indicator


# In[11]:


def read_table_two(soup, table_number):
    
    flat_list = _read_table(table_number, soup)
    
    _list = []
    dict_keys = []
    dict_values = []
    
    logging.debug(f"Length of flat_list is: {len(flat_list)}.")
    logging.debug(f"flat_list is: {flat_list}.")
    
    next_line_pattern = '\\n[\\t]+'
    max_range_pattern = ' Max Range: '
    
    for i in range(len(flat_list)):
        _list_val = flat_list[i]
        if check_pattern_existence(max_range_pattern, _list_val) and         check_pattern_existence(next_line_pattern, _list_val):
            _sublist_2 = _list_val.split(' Max Range: ')
            _sublist = re.split('\\n[\\t]+', _sublist_2[0])
            _sublist.append(_sublist_2[1]) #Specific to this context
            _list.append(_sublist)
        else:
            _list.append([_list_val])
    
    for i in range(len(_list)):
        dict_keys_template = [f'Sensor {i+1} Name', f'Sensor {i+1} Type', f'Sensor {i+1} Max Range']
        for j in range(len(_list[i])):
            dict_keys.append(dict_keys_template[j])
            dict_values.append(_list[i][j])
    
    _dict = dict(zip(dict_keys, dict_values))
    
    df_table_2 = pd.DataFrame().append(_dict, ignore_index=True)
    
    return df_table_2


# In[12]:


def read_table_three(soup, table_number):
    flat_list = _read_table(table_number, soup)
    
    _list = []
    dict_keys = []
    dict_values = []

    next_line_pattern = '\\n[\\t]+'
    
    for i in range(len(flat_list)):
        logging.debug(f"i:{i}")
        _list_val = flat_list[i]
        _sublist = re.split(next_line_pattern, _list_val)
        _sublist_2 = _sublist[-1].split(". ")
        _sublist_2 = [i for i in _sublist_2 if i]
        _list.append(_sublist)
        _list.append(_sublist_2)

        weapon_keys = []
        weapon_values = []

        dict_keys_template = [f'Weapon {i+1} Name', f'Weapon {i+1} Description']
        logging.debug(f"_list:{_list}")
        logging.debug(f"_sublist_2:{_sublist_2}")
        if len(_sublist_2) > 1:
            for j in range(len(_sublist_2)):
                _sublist_3 = _sublist_2[j].split(":")
                weapon_key = f"Weapon {i+1} {_sublist_3[0]}"
                weapon_value = _sublist_3[1]
                weapon_keys.append(weapon_key)
                weapon_values.append(weapon_value)
                logging.debug(f"weapon_keys: {weapon_keys}")
                logging.debug(f"weapon_values: {weapon_values}")


            row_keys = dict_keys_template + weapon_keys
            row_values = _sublist[:2] + weapon_values

        elif len(_sublist_2) == 1 :
            weapon_key = f"Weapon {i+1}"
            weapon_keys.append(weapon_key)
            weapon_value = _sublist_2[0]
            weapon_values.append(weapon_value)
            logging.debug(f"weapon_keys: {weapon_keys}")
            logging.debug(f"weapon_values: {weapon_values}")

            row_keys = dict_keys_template
            row_values = _list[i]


        dict_keys = dict_keys + row_keys
        dict_values = dict_values + row_values
        logging.debug(f"dict_keys: {dict_keys}")
        logging.debug(f"dict_values: {dict_values}")
    
    _dict = dict(zip(dict_keys, dict_values))

    df_table_3 = pd.DataFrame().append(_dict, ignore_index=True)
    
    return df_table_3


# In[13]:


def read_image(soup, url):
    images = soup.findAll('img')
    #insert logic to choose correct index of image from images list
    image_url = images[1]['src']
    complete_url = f'{url}{image_url}'
    
    #perhaps insert try catch logic here to cater for exceptions
    image_data = requests.get(complete_url).content
    
    logging.debug(f'Image data recieved from URL.')
    
    return image_data


# In[14]:


def save_image(image_data, image_output_dir, image_name, image_type):
    with open(f'{image_output_dir}{image_name}.{image_type}', 'wb') as handler:
        handler.write(img_data)
    logging.debug(f'Image written to file: {image_output_dir}{image_name}.{image_type}')


# In[15]:


def combine_tables_into_dataframe(df_to_combine):
#     Something along these lines - but better naming convention:
#     aircraft_data['Name'] = df_aircraft['Link'][0]
#     aircraft_data = pd.concat([df_table_1, df_table_2, df_table_3], axis=1, sort=False)
    aircraft_data = pd.concat(df_to_combine, axis=1, sort=False)
    logging.debug(f"The final df looks like:")
    logging.debug(f"{aircraft_data}")
    return aircraft_data


# In[16]:


def write_dataframe_to_file(dataframe, csv_output_dir, csv_output_filename):
    logging.info(f'...File {csv_output_filename}.csv is being written to disk...')
    dataframe.to_csv(f'{csv_output_dir}{csv_output_filename}.csv', index=False)
    logging.info(f'Writing complete.')


# In[17]:


def main():
    aircraft_url_input_dir = '../data/01_raw/aircraft_url.txt'
    csv_output_dir = '../data/02_intermediate/'
    csv_output_filename = 'aircraft_data'
    image_output_dir = '../data/01_raw/weapons_images/'
    image_type = 'jpg'
    root_url = 'http://cmano-db.com/'
    
    logging.info(f'Beginning Process.')
    
    df_aircraft_urls, aircraft_url_list = get_aircraft_urls(root_url, aircraft_url_input_dir)
    
    aircraft_url_list = aircraft_url_list[:20]
    
    aircraft_data = pd.DataFrame()
    
    for index in range(len(aircraft_url_list)):
        
        url = aircraft_url_list[index]
        
        logging.debug(f'Current URL being processed is: {url} at index: {index}.')
        soup = get_soup_object(url)
        
        number_of_tables, table_header_dict = count_tables_on_page(soup)
        
        df_to_combine = []
        
        for table_number in range(number_of_tables):
            
            logging.debug(f"table_number is {table_number}")
            logging.debug(f"table_header_dict is {table_header_dict}")
            
            _index = table_header_dict['index'][table_number]
            _header = table_header_dict['header'][table_number][0]
            
            logging.debug(f"_index is {_index}")
            logging.debug(f"_header is {_header}")
            
            if _header == "General data:":      
                df_table_1 = read_table_one(soup, table_number)
                logging.debug(f'Table 1 returned successfully.')
                df_to_combine.append(df_table_1)
            elif _header == "Sensors / EW:":
                df_table_2 = read_table_two(soup, table_number)
                logging.debug(f'Table 2 returned successfully.')
                df_to_combine.append(df_table_2)
            elif _header == "Weapons / Loadouts:":
                df_table_3 = read_table_three(soup, table_number)
                logging.debug(f'Table 3 returned successfully.')
                df_to_combine.append(df_table_3)
            _aircraft_data = combine_tables_into_dataframe(df_to_combine)
            logging.debug(f'Table 1, 2 and 3 combined successfully.')       
        aircraft_data = pd.concat([aircraft_data, _aircraft_data])
        logging.debug(f'Row {index} appended to dataframe.')
  
    write_dataframe_to_file(aircraft_data, csv_output_dir, csv_output_filename)

    logging.info(f'Process Complete.')


# In[18]:


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




