import logging
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd
import re


logging.basicConfig(level=logging.DEBUG)


def _get_response(url):
    try:
        response = requests.get(url)
    except error as e:
        logging.error(f"Unable to get response from URL: {url}. \n {e}")
    return response


def get_soup_object(url):
    response = _get_response(url)
    try:
        soup = BeautifulSoup(response.text, "html.parser")
    except error as e:
        logging.error(f"Unable to get response from URL: {url}. \n {e}")

    return soup


def get_aircraft_urls(url, aircraft_url_input_dir):
    try:
        df_aircraft_urls = pd.read_table(aircraft_url_input_dir)
    except FileNotFoundError as e:
        logging.error(f"{e}. Ensure filename is correct and file is stored in correct directory.")

    aircraft_url_list = []
    for index in range(len(df_aircraft_urls)):
        url_suffix_aircraft = df_aircraft_urls['URL'][index]
        aircraft_url_list.append(f'{url}{url_suffix_aircraft}')
    logging.debug(f'URLs read in successfully.')
    return df_aircraft_urls, aircraft_url_list


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


def _get_table_header(table, index_list, header_list):
    
    for i in range(len(table)):
        header = table[i].find_all('th')
        header_string = [i.text for i in header]
        index_list.append(i)
        header_list.append(header_string)
        logging.debug(f"Index: {i}")
        logging.debug(f"Header: {header_string}")
    
    return index_list, header_list


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


def check_pattern_existence(pattern, string):
    if re.search(pattern, string):
        indicator = True
    else:
        indicator = False
    
    return indicator


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
        if check_pattern_existence(max_range_pattern, _list_val) and \
                check_pattern_existence(next_line_pattern, _list_val):
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


def read_image(soup, url):
    images = soup.findAll('img')
    #insert logic to choose correct index of image from images list
    image_url = images[1]['src']
    complete_url = f'{url}{image_url}'
    
    #perhaps insert try catch logic here to cater for exceptions
    image_data = requests.get(complete_url).content
    
    logging.debug(f'Image data recieved from URL.')
    
    return image_data


def save_image(image_data, image_output_dir, image_name, image_type):
    with open(f'{image_output_dir}{image_name}.{image_type}', 'wb') as handler:
        handler.write(img_data)
    logging.debug(f'Image written to file: {image_output_dir}{image_name}.{image_type}')


def combine_tables_into_dataframe(df_to_combine):
    aircraft_data = pd.concat(df_to_combine, axis=1, sort=False)
    logging.debug(f"The final df looks like:")
    logging.debug(f"{aircraft_data}")
    return aircraft_data


def write_dataframe_to_file(dataframe, csv_output_dir, csv_output_filename):
    logging.info(f'...File {csv_output_filename}.csv is being written to disk...')
    dataframe.to_csv(f'{csv_output_dir}{csv_output_filename}.csv', index=False)
    logging.info(f'Writing complete.')


def main():
    aircraft_url_input_dir = '../data/01_raw/aircraft_url.txt'
    csv_output_dir = '../data/02_intermediate/'
    csv_output_filename = 'aircraft_data'
    image_output_dir = '../data/01_raw/weapons_images/'
    image_type = 'jpg'
    root_url = 'http://cmano-db.com/'
    
    logging.info(f'Beginning Process.')
    
    df_aircraft_urls, aircraft_url_list = get_aircraft_urls(root_url, aircraft_url_input_dir)

    #TODO: Remove line below in final version:
    aircraft_url_list = aircraft_url_list[:500]
    
    aircraft_data = pd.DataFrame()
    
    for index in range(len(aircraft_url_list)):

        if (index+1) % 100 == 0:

            time.sleep(3)

        url = aircraft_url_list[index]

        logging.info(f'Current URL being processed is: {url} at index: {index}.')
        soup = get_soup_object(url)

        number_of_tables, table_header_dict = count_tables_on_page(soup)

        df_to_combine = []

        if 4 > number_of_tables > 0:

            for table_number in range(number_of_tables):

                logging.debug(f"table_number is {table_number}")
                logging.debug(f"table_header_dict is {table_header_dict}")

                _index = table_header_dict['index'][table_number]
                _header = table_header_dict['header'][table_number][0]

                logging.debug(f"_index is {_index}")
                logging.debug(f"_header is {_header}")

                if _header == "General data:":
                    #Insert logic here to catch exceptions
                    df_table_1 = read_table_one(soup, table_number)
                    logging.debug(f'Table 1 returned successfully.')
                    df_to_combine.append(df_table_1)
                elif _header == "Sensors / EW:":
                    #Insert logic here to catch exceptions
                    df_table_2 = read_table_two(soup, table_number)
                    logging.debug(f'Table 2 returned successfully.')
                    df_to_combine.append(df_table_2)
                elif _header == "Weapons / Loadouts:":
                    #Insert logic here to catch exceptions
                    df_table_3 = read_table_three(soup, table_number)
                    logging.debug(f'Table 3 returned successfully.')
                    df_to_combine.append(df_table_3)
            _aircraft_data = combine_tables_into_dataframe(df_to_combine)
            logging.debug(f'Table 1, 2 and 3 combined successfully.')
        else:
            logging.error(f"For this aircraft: {url}, the number of tables found is: {number_of_tables}")

        try:
            _aircraft_data = combine_tables_into_dataframe(df_to_combine)
            logging.debug(f'Table 1, 2 and 3 combined successfully.')

            aircraft_data = pd.concat([aircraft_data, _aircraft_data])
            logging.debug(f'Row {index} appended to dataframe.')
        except error as e:
            logging.error(f"Aircraft {url} at index {index} was not added to data.")
  
    write_dataframe_to_file(aircraft_data, csv_output_dir, csv_output_filename)

    logging.info(f'Process Complete.')


if __name__ == '__main__':
    main()