from logging import PlaceHolder
from time import time
import streamlit as st
import requests
from streamlit_lottie import st_lottie
import tempfile
import cv2
from PIL import Image
from Cookie import *
import numpy as np


@st.cache_resource()
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    else:
        return r.json()

def extract_Background(vid_name , cookie ):
    vid_cap = cv2.VideoCapture(vid_name)
    success,image = vid_cap.read()
    image = cv2.resize(image,(640,512),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
    cam_img_name = r'images\background_img.jpeg'
    cv2.imwrite( cam_img_name , image)
    cookie.set('background_image', cam_img_name)



def save_downsize_video(video_file,banner,cookie):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    vid_cap = cv2.VideoCapture(tfile.name)
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    cookie.set('fps',fps)
    banner.info("Video is being uploaded to the app")
    extract_Background( tfile.name , cookie)

    writer = None
    while (vid_cap.isOpened()):
        success, image = vid_cap.read()
        if success:
            if writer is None:
                vid_name = r'videos\pde\{}'.format(video_file.name)
                fourcc =  cv2.VideoWriter_fourcc(*'H264')
                writer = cv2.VideoWriter(vid_name,fourcc,  fps , (1920,1024))

            frame = cv2.resize(image,(1920,1024),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            writer.write(frame)
        else:
            vid_cap.release()
            break
    writer.release()
    cookie.set('video', vid_name)


def app():
    cookie = Cookie()
    col1, col2 = st.columns(2)
    
    with col1:
        st.title("Welcome to Tracker")
        #there is a video in the cookie
        banner = st.empty()
        if cookie.get('video') is not None:
            st.write("There is a Video cached in the Cookie!")
            st.image(cookie.get('background_image'),width=300)
            st.write(cookie.get("video"))
            delete = st.button("Upload New Video")
            if delete:
                cookie.delete("video")
                st.experimental_rerun()
        
        #if want to upload new vide
        else:
            video_file = st.file_uploader(label='Upload video', type=['mp4', 'avi'] , key='vid')
            if video_file:
                save_downsize_video(video_file , banner , cookie)
                banner.empty()
                banner.success("Done")
                st.experimental_rerun()
        
        if cookie.get("sat_image") is None:
            img_file = st.file_uploader(label='Satelite Image', type=['png', 'jpg','jpeg'] ,key='img')
            ppm = st.number_input("pixels per meter",key="pixelpermeter")
            if img_file:
                img = Image.open(img_file)
                width , height = img.size
                size = ( 640,512  )
                cookie.set("scale_w" , width/size[0] )
                cookie.set("scale_h" , height/size[1] )
                sat_image = img.resize(size)
                sat_img_name = 'images/sat_img.png'
                sat_image.save(sat_img_name)
                cookie.set('sat_image' , sat_img_name)
                confirm = st.button("confirm")
                if confirm:
                    cookie.set('ppm', ppm)
                    st.experimental_rerun()
        else:
            st.write("There is a Satelite images in the Cookie!")
            st.image(cookie.get('sat_image'),width=300)
            st.write("pixel permete" ,cookie.get("ppm"))
            delete = st.button("Upload New Satelite image")
            if delete:
                cookie.delete("sat_image")
                cookie.delete("ppm")
                st.experimental_rerun()

    with col2:
        lottie = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_yvrh9cry.json")
        st_lottie(lottie)
    