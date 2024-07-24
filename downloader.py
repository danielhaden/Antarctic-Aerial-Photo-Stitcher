from bs4 import BeautifulSoup
from PIL import Image
import requests
import urllib.request
import os
import re
import shutil
import json
import time
import cv2

base_url = 'https://data.pgc.umn.edu/aerial/usgs/tma/photos/med/'
base_dir = '/Users/dhadenx6/Desktop/antarctic_tma/'

def extract_table(url, rm_slash=False):
    html = requests.get(url).text
    bs = BeautifulSoup(html)
    table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=='indexlist')
        
    items = []
    for tr in table.find_all(lambda tag: tag.name=='a'):
        angle_id = tr.text
        if angle_id[:2] == 'CA':

            if rm_slash:
                items.append(re.sub(r'/', '',tr.text))

            else:
                items.append(tr.text)

    return items

def get_images(run_id, base_url='https://data.pgc.umn.edu/aerial/usgs/tma/photos/med/'):
    run_angles = extract_table(base_url + run_id)
    run_dir = base_dir + run_id

    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    for run in run_angles:
        if re.search(r'L', run):
            angle_type = r'L'
            angle_run_dir = run_dir + '/left/'
            if not os.path.exists(angle_run_dir):
                os.mkdir(angle_run_dir)

        elif re.search(r'V', run):
            angle_type = r'V'
            angle_run_dir = run_dir + '/vertical/'
            if not os.path.exists(angle_run_dir):
                os.mkdir(angle_run_dir)

        elif re.search(r'R', run):
            angle_type = r'R'
            angle_run_dir = run_dir + '/right/'
            if not os.path.exists(angle_run_dir):
                os.mkdir(angle_run_dir)
                
        run_angle_url = base_url + run_id + '/' + run

        photos = extract_table(run_angle_url)

        for filename in photos:
            photo_id = re.split(angle_type, filename)[1]

            if not re.search(r'X', photo_id):
                urllib.request.urlretrieve(run_angle_url + filename, angle_run_dir + photo_id)


def stitch_together(run_id, image_id):
    return

def image_folder_to_video(dir_path):
    run_id = os.path.basename(os.path.dirname(dir_path))
    angle_type = os.path.basename(os.path.normpath(dir_path))

    images = []
    for f in os.listdir(dir_path):
        if f.endswith('tif'):
            images.append(f)

    images.sort()

    # Determine the width and height from the first image
    image_path = os.path.join(dir_path, images[0])

    frame = cv2.imread(image_path)
    cv2.imshow('video',frame)
    height, width, channels = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Be sure to use lower case
    out = cv2.VideoWriter(os.path.dirname(dir_path) +  "/" + run_id + "-" + angle_type + ".mp4", fourcc, 5.0, (width, height))

    for image in images:

        image_path = os.path.join(dir_path, image)
        frame = cv2.imread(image_path)

        out.write(frame) # Write out frame to video

        cv2.imshow('video',frame)
        
    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()

def convert_all_image_folders_to_video(run_id):
    dir_path = base_dir + run_id

    for angle in os.listdir(dir_path):
        run_path = os.path.join(dir_path, angle)
        if os.path.isdir(run_path):
            image_folder_to_video(run_path)

# convert_all_image_folders_to_video("CA3152")

    
def delete_images(dir_path, verbose=False):

    if verbose:
        print("deleting image folders in " + dir_path)
    
    for angle in ['/left', '/vertical', '/right']:
        try:

            shutil.rmtree(dir_path + angle)

        except:
            print("could not delete folder: " + angle)
        

def save_local_tracking(local_dict):
    with open("/Users/dhadenx6/Desktop/antarctic_tma/run-data.json", "w") as data_file:
        json.dump(local_dict, data_file)
            
def process_run(run_id, local_tracking=None, verbose=True):
    print("downloading images for run: " + run_id)
    get_images(run_id)
    dir_path = base_dir + run_id
    convert_all_image_folders_to_video(run_id)
    delete_images(dir_path, verbose=verbose)
    print("processed images of " + run_id)

    if local_tracking != None:
        local_tracking[run_id]['processed'] = True
        local_tracking[run_id]['processed_date'] = time.time()
        save_local_tracking(local_tracking)


def batch_process(batch_count = 10):
    run_data = load_local_history()

    unprocessed_runs = {k: v for k, v in run_data.items() if v["processed"] != True}
    runs_to_process = list(unprocessed_runs.keys())[:batch_count]

    for run_id in runs_to_process:
        process_run(run_id, local_tracking=run_data, verbose=True)
    
batch_process()      
# process_run("CA3152")

  
def list_runs():
    runs = extract_table(base_url, rm_slash=True)
    return runs

def init_track_runs_locally():
    runs = list_runs()

    run_info = {}
    for run in runs:
        run_info[run] = { 'processed': False,
                          'processed date': None }

    with open("/Users/dhadenx6/Desktop/antarctic_tma/run-data.json", "w") as data_file:
        json.dump(run_info, data_file)

def load_local_history():
    with open("/Users/dhadenx6/Desktop/antarctic_tma/run-data.json", "r") as data_file:
        run_data = json.load(data_file)
        return run_data

# runs = load_local_history()


        
# init_track_runs_locally()
# download_all('CA0551')
#image_folder_to_video('/Users/dhadenx6/Desktop/antarctic_tma/CA0551/left')
# delete_images('/Users/dhadenx6/Desktop/antarctic_tma/CA0551')

# get_pics("CA0551", "L",  '/Users/dhadenx6/Desktop/antarctic_tma/' + run_id + "/left")

# pic_urls = base_url + 'CA0551' + '/CA055131L'))
# print(get_one_angle_series_for_run('CA055131L'))
