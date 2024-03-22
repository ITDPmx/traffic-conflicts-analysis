import random

def mock_data():
    locations = []
    raw_images = []
    processed_images = []
    jetson_devices = []

    for i in range(5):
        locations.append((i, f'location {i}'))
    
    for loc in locations:
        jetson_devices.append((loc[0], f'http://172.28.17.104/devices/jetson{loc[0]}', f'jetson_{loc[0]}'))

    for idev, dev in enumerate(jetson_devices):
        loc = locations[idev]
        for i in range(15):
          taken_at = random.randint(1680000000000, 1684000000000)
          raw_images.append((f'{dev[0]}_{i}', f'{loc[0]}', dev[0], dev[1], taken_at, f'http://crowd-counting-bucket.s3-website-east1.amazonaws.com/{dev[0]}_{i}'))
          processed_images.append((f'processed_{dev[0]}_{i}', f'{loc[0]}', f'{dev[0]}_{i}', random.randint(0,15), taken_at))
    
    json = '{'
    json += '"locations": ['
    for i, loc in enumerate(locations):
        json += f'{{ "id": {loc[0]}, "short_name": "{loc[1]}" }}'
        if i != len(locations) - 1:
            json += ','
        json += '\n'
    json += '],\n'
    json += '"jetson_devices": ['
    for i, dev in enumerate(jetson_devices):
        json += f'{{ "id": {dev[0]}, "source_url": "{dev[1]}", "model_name": "{dev[2]}" }}'
        if i != len(jetson_devices) - 1:
            json += ','
        json += '\n'
    json += '],\n'   
    json += '"processed_images": ['
    for i, img in enumerate(processed_images):
        json += f'{{ "id": "{img[0]}", "location_id": "{img[1]}", "raw_image_id": "{img[2]}", "people_count": {img[3]}, "taken_at": {img[4]} }}'
        if i != len(processed_images) - 1:
            json += ','
        json += '\n'
    json += '],\n'     
    json += '"raw_images": ['
    for i, img in enumerate(raw_images):
        json += f'{{ "id": "{img[0]}", "location_id": "{img[1]}", "device_id": "{img[2]}", "camera_source": "{img[3]}", "taken_at": {img[4]}, "photo_url": "{img[5]}" }}'
        if i != len(raw_images) - 1:
            json += ','
        json += '\n'
    json += ']\n'       
    json += '}'
    with open('data.json', 'w') as json_file:
      json_file.write(json)

mock_data()
