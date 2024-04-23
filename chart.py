import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np 
import datetime
import cv2

class Chart:

    @staticmethod
    def generate_pie(classes_count,classes_names):
        dataframe = pd.DataFrame(classes_count,index = [0])
        fig = px.pie(dataframe,names=classes_names,values = dataframe.loc[0].values)
        fig.update_traces(marker=dict(colors=px.colors.sequential.Mint))
        path = 'charts/pie/{}.jpg'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        fig.write_image(path ,'jpg',scale = 1.5)
        return path 

    @staticmethod
    def generate_bar(data,type):
        fig, ax = plt.subplots()
        ax.bar(data.keys(),data.values())
        plt.xticks(rotation = 45,ha = 'right')
        ax.set_title('{} average for each class'.format(type))    
        ax.set_ylabel('{}'.format(type)) 
        path = "charts/{}/{}.png".format(type,datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        plt.savefig(path)
        return path
    
    
        