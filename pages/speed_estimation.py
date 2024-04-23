from traffic_speed_est import map,  index, transform,track
from streamlit_option_menu import option_menu
import streamlit as st

st.set_page_config(layout="wide")

if st.session_state['role']=='police Department employee':
    if 'pages' not in st.session_state.keys():
        st.session_state['pages'] = { 'Home' : ( index.app , 'house' ),
        'Map' : (map.app , 'geo'),
            'Transform' : (transform.app , 'arrow-left-right'),
            'Track': (track.app , 'car-front' )

        }
    if 'current page' not in st.session_state.keys():
        st.session_state['current page'] = 0
    icons = list( st.session_state['pages'].values())

    col1 ,col2 = st.columns([10,1])
    with col1:
        selected = option_menu(
            None, list(st.session_state['pages'].keys()), 
            icons= [ x[1] for x in icons] , 
            menu_icon="cast", default_index=st.session_state['current page'], orientation="horizontal")

    st.session_state['pages'][selected][0]()
else:
    st.title("your are not allowed to enter")
