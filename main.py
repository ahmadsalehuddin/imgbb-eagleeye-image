import csv
import os
import requests
from tabulate import tabulate
import urllib.parse

import imgbb

def read_entities_csv():
    entities_csv_path = './input/entities.csv' # Configuration
    data = []
    with open(entities_csv_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader, None) # Skip column headers
        for row in csv_reader:
            data.append(row)
    return [item for item in data]

def search_entities_ee(entity_name):
    ee_search_endpoint = 'http://instabi.datamicron.com:9020/search/' # Configuration
    encoded_entity_name = urllib.parse.quote(entity_name)
    api_url = ee_search_endpoint + encoded_entity_name
    response = requests.get(api_url)
    return response.json()

def print_entities_in_tabular(data):
    ids_names = [[item['objectId'], item['name']] for item in data]
    column_headers = ['Entity ID', 'Entity Name']
    print(tabulate(ids_names, headers=column_headers) + '\n')

def get_entities_ee(entity_name):
    search_result = search_entities_ee(entity_name)
    result_size = len(search_result)

    entities_ee = []
    if result_size == 1:
        id, name = search_result[-1]['objectId'], search_result[-1]['name']
        entities_ee.append([id, name])
        return entities_ee
    elif result_size > 1:
        print(f"We found {result_size} entities that contain '{entity_name}'.\n")
        print_entities_in_tabular(search_result)
        print("Warning! This action would be applied to all entities OR only one entity (if the correct entity ID is provided).")
        entity_id_input = input("Please provide an ID or skip [ENTER] to apply to all: ")

        if entity_id_input.strip():
            entities_ee = [[item['objectId'], item['name']] for item in search_result if item['objectId'] == entity_id_input]
        
        if len(entities_ee) == 0:
            entities_ee = [[item['objectId'], item['name']] for item in search_result]
        return entities_ee
    else:
        print(f'{entity_name} does not exist. Skipping to the next entity...')

def build_image_path(image_filename):
    root_folder = './input/images' # Configuration
    image_filepath = os.path.join(root_folder, image_filename)
    image_ext = os.path.splitext(image_filepath)[-1]
    is_file_exist = os.path.exists(image_filepath) and os.path.isfile(image_filepath)
    is_image_valid = image_ext in ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.webp', '.heic', '.pdf') if is_file_exist else False
    is_image_small = os.path.getsize(image_filepath) < 33554432 if is_file_exist else False
    
    if not is_image_valid:
        print('Image file is invalid.')
        return
    
    if not is_image_small:
        print('Image file is too big.')
        return

    return image_filepath

def update_ee_entity_images(entity_id, imgbb_url):
    ee_object_endpoint = 'http://instabi.datamicron.com:9020/kbdata/Object/' # Configuration
    api_url = ee_object_endpoint + entity_id
    api_params = {
        'imageUrl': imgbb_url
    }
    requests.post(api_url, api_params)


entities_csv = []
entities_csv = read_entities_csv()

for csv_entity_name, csv_image_filename in entities_csv:
    entities_ee = get_entities_ee(csv_entity_name)
    for ee_entity_id, ee_entity_name in entities_ee:
        image_path = build_image_path(csv_image_filename)
        response = ''
        if image_path:
            response = imgbb.upload_image(ee_entity_name, image_path)
        if response['status'] == 200:
            imgbb_url = response['data']['url']
            imgbb_delete_url = imgbb_url = response['data']['delete_url']
            imgbb.save_imgbb_csv(ee_entity_id, ee_entity_name, imgbb_url)
            update_ee_entity_images(ee_entity_id, imgbb_url)