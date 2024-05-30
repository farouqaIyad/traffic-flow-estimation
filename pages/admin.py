from admin import users_prediction, speed_estimation
from streamlit_option_menu import option_menu
import streamlit as st
import cv2

st.set_page_config(layout="wide")

if st.session_state["role"] == "Admin":
    if "pages" not in st.session_state.keys():
        st.session_state["pages"] = {
            "users_predictions": (users_prediction.app, ""),
            "speed_estimation": (speed_estimation.app, ""),
        }
    if "current page" not in st.session_state.keys():
        st.session_state["current page"] = 0
    icons = list(st.session_state["pages"].values())

    col1, col2 = st.columns([10, 1])
    with col1:
        selected = option_menu(
            None,
            list(st.session_state["pages"].keys()),
            icons=[x[1] for x in icons],
            menu_icon="cast",
            default_index=st.session_state["current page"],
            orientation="horizontal",
        )

    st.session_state["pages"][selected][0]()
else:
    st.title("your are not allowed to enter")
