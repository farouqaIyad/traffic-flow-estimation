from video_processor import VideoProcessor
from functions import generate_bar_chart
from supervision import Detections
from db import user_images_db
from ultralytics import YOLO
import plotly.express as px
from pytube import YouTube
from chart import Chart
from model import Model
import streamlit as st
import pandas as pd 
import settings
import datetime


def load_model(model_path):
    model = YOLO(model_path)
    model.to('cuda')
    return model

def play_youtube_video(conf, model_path,col3):
    
    source_youtube = st.text_input("YouTube Video url")
    yt = YouTube(source_youtube)
    stream = yt.streams.filter(file_extension="mp4", res=720).first()
    if st.button('Detect Objects'):
        with col3:
            model = Model(model_path,conf,device = 'cuda')
            video = VideoProcessor(stream.url,model)
            video.process()

        
def play_stored_video(conf, model_path,col,col2,col3):

    with col:
        source_vid = st.selectbox(
            "Choose a video...", settings.VIDEOS_DICT.keys())
        
    source_video_path=r"{}".format(settings.VIDEOS_DICT.get(source_vid))
    with col2:
        with open(settings.VIDEOS_DICT.get(source_vid), 'rb') as video_file:
            video_bytes = video_file.read() 
        if video_bytes:
            st.video(video_bytes)

    if st.button('Detect Video Objects'):
        with col3:
            model = Model(model_path,conf,device = 'cuda')
            video = VideoProcessor(source_video_path,model)
            video.process()
            pie_chart = Chart.generate_pie(video.classes_count,video.classes_names)
            st.image(pie_chart)
        with col2:
            bar_chart = Chart.generate_bar(video.confidence_averages,'conf')
            st.image(bar_chart)


        
def image_handler(model_choice,model,image,conf,col2,col3):
    
    with col3:                        
        results = model.predict(image,conf=conf)[0]
        detections = Detections.from_ultralytics(results)
        confidence_scores = detections.confidence
        class_names = list(model.model.names.values())
        classes = {i: 0 for i in class_names}
        confs = {i: 0 for i in class_names}
        detecitonsAndConfs = zip(detections.class_id,confidence_scores)
        for class_id,conf in detecitonsAndConfs :
            classes[class_names[class_id]]+=1
            confs[class_names[class_id]]+=conf
        for i in class_names:
            confs[i]=(confs[i]/classes[i]) if classes[i] != 0 else 0
        res_plotted = results.plot()[:, :, ::-1]
        st.image(res_plotted, caption='Detected Image',
                use_column_width=True)
        pie_chart_path = Chart.generate_pie(classes,class_names)
        st.image(pie_chart_path)
        bar_chart_path = Chart.generate_bar(confs,'conf')
        input_image_path = r'images\inputs\{}.jpg'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        image.save(input_image_path)
        user_images_db.insert_one({"input_image":input_image_path,
                                   "pie_chart":pie_chart_path,
                                   "bar_chart":bar_chart_path,
                                   "model_type":model_choice
        })
    with col2:
        st.image(bar_chart_path)
        