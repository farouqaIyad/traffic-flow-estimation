from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from functions import load_lottieurl
from user import login, signup
import streamlit as st

st.set_page_config(page_title="farouq", layout="wide")

st.markdown(
    """ <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
.reportview-container { margin-top: -em; }
menu { width : 100wh; }
</style> """,
    unsafe_allow_html=True,
)


st.sidebar.success("select a page above.")
st.markdown("###")
st.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
c, c1, c2 = st.columns([2, 5, 4])
st.set_option("deprecation.showPyplotGlobalUse", False)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "role" not in st.session_state:
    st.session_state["role"] = ""

if not st.session_state["logged_in"]:
    with st.sidebar.empty():
        selected_option = option_menu(
            menu_title="Navigation",
            menu_icon="list-columns-reverse",
            icons=["box-arrow-in-right", "person-plus"],
            options=["Login", "Create Account"],
            styles={
                "container": {"padding": "5px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0px",
                },
            },
        )

    if selected_option == "Login":
        with c1:
            login()
        with c2:
            lottie_json = load_lottieurl(
                "https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json"
            )
            st_lottie(lottie_json)

    elif selected_option == "Create Account":
        with c1:
            signup()
        with c2:
            lottie_json = load_lottieurl(
                "https://lottie.host/4954f2b6-8c0f-4e31-93f8-a5a4aa7a7ab5/LFeiNig55W.json"
            )
            st_lottie(lottie_json)
else:
    st.title("you are already logged in")
