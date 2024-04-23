import streamlit as st
from db import pde_admin_db
import cv2

def app():
    col1, col2, col3 = st.columns(3)
    documents = pde_admin_db.find()
    for doc in documents:
        with col1:
            vid_cap = cv2.VideoCapture(doc['video_path'])
            success,img = vid_cap.read()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            st.image(img)
        with col2:
            img = cv2.imread(doc['heat_map'])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            st.image(img)
        with col3:
            img = cv2.imread(doc['conf_average'])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            st.image(img)
        
