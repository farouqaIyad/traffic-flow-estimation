import streamlit as st
from db import user_images_db


def app():
    col1, col2, col3 = st.columns(3)
    images = user_images_db.find()
    for image in images:
        with col1:
            st.image(image['input_image'])
            st.write(image['model_type'])
        with col2:
            st.image(image['pie_chart'])
            st.markdown('###')
            st.markdown('###')

        with col3:  
            st.image(image['bar_chart'])