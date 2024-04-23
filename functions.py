from time import time
import streamlit as st
import requests
import cv2
from Cookie import *
import numpy as np
import re 
import matplotlib.pyplot as plt
import datetime


def set_cookie(cookie,name,polygon):
    zone_in_str = ",".join(arr.tobytes().hex() for arr in polygon)
    cookie.set(name,zone_in_str)
    
    
def get_cookie(cookie,name):
    zone_in_str = cookie.get(name)
    if zone_in_str:
        zones_in_list = [np.frombuffer(bytes.fromhex(data),dtype=np.int64).reshape(-1,2)for data in zone_in_str.split(",")]
        return zones_in_list
    else:
        return "cookie is empty"
    

@st.cache_resource()
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    else:
        return r.json()


def check_valid_name(name_sign_up: str) -> bool:
    """
    Checks if the user entered a valid name while creating the account.
    """
    name_regex = (r'^[A-Za-z_][A-Za-z0-9_]*')

    if re.search(name_regex, name_sign_up):
        return True
    return False


def check_valid_email(email_sign_up: str) -> bool:
    """
    Checks if the user entered a valid email while creating the account.
    """
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email_sign_up):
        return True
    return False


def non_empty_str_check(username_sign_up: str) -> bool:
    """
    Checks for non-empty strings.
    """
    empty_count = 0
    for i in username_sign_up:
        if i == ' ':
            empty_count = empty_count + 1
            if empty_count == len(username_sign_up):
                return False

    if not username_sign_up:
        return False
    return True


def generate_heatmap(image,boxes):
    image = np.asarray(image)
    heatmap = np.zeros_like(image[:,:,0])
    for box in boxes:
        x1,y1,x2,y2 = box.astype(int)
        center_x = int((x1+x2)/2)
        center_y = int((y1+y2)/2)
        heatmap[center_y,center_x]+=1
        for i in range(-3,4):
            for j in range(-3,4):
                if 0 <= center_y + i < heatmap.shape[0] and 0<= center_x + j <heatmap.shape[1]:
                    heatmap[center_y + i,center_x + j]+=1
    heatmap = (heatmap-heatmap.min())/(heatmap.max()-heatmap.min())
    heatmap_image = (heatmap * 255).astype(np.uint8)
    heatmap_image_colored = cv2.applyColorMap(heatmap_image, cv2.COLORMAP_JET)
    heatmap_overlay = cv2.addWeighted(image, 0.7, heatmap_image_colored, 0.3, 0)
    path = 'charts/heat/{}.jpg'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    cv2.imwrite(path,heatmap_overlay)
    return path 


def generate_bar_chart(data,type):
    fig, ax = plt.subplots()
    ax.bar(data.keys(),data.values())
    plt.xticks(rotation = 45,ha = 'right')
    ax.set_title('{} average for each class'.format(type))    
    ax.set_ylabel('{}'.format(type)) 
    path = "images/conf/{}.png".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    plt.savefig(path)
    return path

    


