from streamlit_lottie import st_lottie
from functions import load_lottieurl
import streamlit as st
from Cookie import *
import tempfile
import cv2


def extract_Background(vid_name, cookie):
    vid_cap = cv2.VideoCapture(vid_name)
    success, image = vid_cap.read()
    cookie.set("tunnel_image", image)


def save_downsize_video(video_file, banner, cookie):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    vid_cap = cv2.VideoCapture(tfile.name)
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    banner.info("Video is being uploaded to the app")
    extract_Background(tfile.name, cookie)
    writer = None
    while vid_cap.isOpened():
        success, image = vid_cap.read()
        if success:
            if writer is None:
                vid_name = r"videos\traffic_analysis\{}".format(video_file.name)
                fourcc = cv2.VideoWriter_fourcc(*"H264")
                writer = cv2.VideoWriter(
                    vid_name, fourcc, fps, (image.shape[1], image.shape[0])
                )

            frame = cv2.resize(
                image,
                (image.shape[1], image.shape[0]),
                fx=0,
                fy=0,
                interpolation=cv2.INTER_CUBIC,
            )
            writer.write(frame)
        else:
            vid_cap.release()
            break
    writer.release()
    cookie.set("tunnel_video", vid_name)


def app():

    cookie = Cookie()
    col1, col2 = st.columns(2)

    with col1:

        st.title("Welcome")

        banner = st.empty()
        if cookie.get("tunnel_video") is not None:
            st.write("There is a Video cached in the Cookie!")
            st.image(cookie.get("tunnel_image"), width=300)
            st.write(cookie.get("tunnel_video"))
            delete = st.button("Upload New Video")
            if delete:
                cookie.delete("tunnel_video")
                st.experimental_rerun()

        else:
            video_file = st.file_uploader(
                label="Upload video", type=["mp4", "avi", "mov"], key="vid"
            )
            if video_file:
                save_downsize_video(video_file, banner, cookie)
                banner.empty()
                banner.success("Done")

    with col2:
        lottie = load_lottieurl(
            "https://assets8.lottiefiles.com/packages/lf20_yvrh9cry.json"
        )
        st_lottie(lottie)
