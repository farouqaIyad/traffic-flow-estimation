from video_processor import VideoAndSpeedProcessor,SpeedProcessor
from Transformer import get_Homogenous_Transform_from_Cookie
from db import pde_admin_db,speeding_cars_db
from distutils.command.config import config
from model import Model
from chart import Chart
import streamlit as st
from Cookie import *
import torch
import cv2


def app():
    cookie = Cookie()
    confidence = st.sidebar.slider('confidence',min_value= 0.0, max_value=1.0,value=0.7) 
    sat_or_road_img =  None
    start = st.button("start tracking")
    video = cookie.get("video")
    sat_or_road_img = cookie.get("sat_image") if sat_or_road_img is None else None
    img = cv2.imread(sat_or_road_img)
    tfrom = get_Homogenous_Transform_from_Cookie()
    col1,col2 = st.columns(2)
    if video is not None and img is not None and tfrom is not None and start:

        with torch.no_grad():
            with col1:
                model = Model(r"C:\Users\NITRO 5\Downloads\best (3).pt",conf =confidence,device='cuda' )
                speed_processor = SpeedProcessor(tfrom)
                video = VideoAndSpeedProcessor(r"{}".format(video),model,speed_processor)
                video.process()
                speed_average_bar_chart = Chart.generate_bar(video.total_cars_speed_average,'speed')
                conf_average_bar_chart = Chart.generate_bar(video.confidence_averages,'conf')
                cv2.imwrite(video.heatmap_path,speed_processor.satilite_image)
                pde_admin_db.insert_one({"heat_map":video.heatmap_path,"video_path":video.source_video_path,"conf_average":conf_average_bar_chart})
                speeding_vehicles = speeding_cars_db.find({'output_video':cookie.get('video')})
                num_speeding_vehicles = speeding_cars_db.count_documents({'output_video': cookie.get('video')})
                
            with col2:
                st.image(speed_average_bar_chart)
        
        if speeding_vehicles:
            speeding_vehicles_list = list(speeding_cars_db.find({'output_video': cookie.get('video')}))
            num_speeding_vehicles = len(speeding_vehicles_list)

            batch_size = 3

            for i in range(0, num_speeding_vehicles, batch_size):
                col1, col2, col3 = st.columns(3)
                batch_index = 0

                for speeding_vehicle in speeding_vehicles_list[i:i+batch_size]:
                    try:
                        col = col1 if batch_index % 3 == 0 else col2 if batch_index % 3 == 1 else col3
                        with col:
                            st.image(speeding_vehicle['image'])  
                            st.write(f"Speed: {speeding_vehicle['Speed']}")  
                            st.write(f"Time: {speeding_vehicle['time']}")
                            batch_index += 1
                    except KeyError:
                        st.write("Error retrieving image or data.")
            
    
       
            



  


    
