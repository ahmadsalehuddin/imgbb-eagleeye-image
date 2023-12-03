import base64
import csv
import os
import requests

def upload_image(entity_name, image_path):
    api_url = 'https://api.imgbb.com/1/upload' # Configuration
    api_key = '0d3c3e4a9a19289e94f133d63b108c5c' # Configuration
    encoded_image = ''
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read())
    api_params = {
        'key': api_key,
        'image': encoded_image,
        'name': entity_name
    }
    response = requests.post(api_url, api_params)
    return response.json()

def save_imgbb_csv(entity_id, entity_name, imgbb_url, delete_url):
    imgbb_csv_path = './output/imgbb.csv' # Configuration
    is_csv_exist = os.path.exists(imgbb_csv_path)

    if not is_csv_exist:
        with open(imgbb_csv_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['entity_id', 'entity_name', 'imgbb_url', 'delete_url'])
            csv_writer.writerow([entity_id, entity_name, imgbb_url, delete_url])
        return

    with open(imgbb_csv_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([entity_id, entity_name, imgbb_url, delete_url])