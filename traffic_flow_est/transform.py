import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from Cookie import *
import numpy as np
from functions import set_cookie


def app():

    cookie = Cookie()

    col1, col2 = st.columns([2, 2])
    drawing_mode = "rect"
    bg_image = cookie.get("tunnel_image")
    image = Image.open(bg_image) if bg_image else None
    banner = st.empty()
    if image is None:
        banner.error("no image")
    else:
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=3,
            stroke_color="#eee",
            background_color="#eee",
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode=drawing_mode,
            display_toolbar=st.sidebar.checkbox("Display toolbar", True),
            key="full_app",
        )

        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data)
        if canvas_result.json_data is not None:
            objects = pd.json_normalize(canvas_result.json_data["objects"])
            if not objects.empty:
                left = objects["left"]
                top = objects["top"]
                right = objects["left"] + objects["width"]
                bottom = objects["top"] + objects["height"]

            if len(left) == 8:
                ZONE_IN_POLYGONS = list()
                ZONE_OUT_POLYGONS = list()
                for i in range(0, 8):
                    if i <= 3:
                        ZONE_IN_POLYGONS.append(
                            np.array(
                                [
                                    [left[i], top[i]],
                                    [right[i], top[i]],
                                    [right[i], bottom[i]],
                                    [left[i], bottom[i]],
                                ]
                            )
                        )
                    else:
                        ZONE_OUT_POLYGONS.append(
                            np.array(
                                [
                                    [left[i], top[i]],
                                    [right[i], top[i]],
                                    [right[i], bottom[i]],
                                    [left[i], bottom[i]],
                                ]
                            )
                        )
                set_cookie(cookie, "zones_in", ZONE_IN_POLYGONS)
                set_cookie(cookie, "zones_out", ZONE_OUT_POLYGONS)
