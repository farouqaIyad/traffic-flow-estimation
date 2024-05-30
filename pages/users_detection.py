import streamlit as st
import settings
import helper
import PIL

if st.session_state["role"] == "User":
    col1, col2, col3 = st.columns([4, 4, 4])
    with col1:
        confidence = float(st.slider("Select Model Confidence", 25, 100, 40)) / 100
        source_radio = st.radio("Select Source", settings.SOURCES_LIST)
        model_choice = st.selectbox("model *", ["vis_drone", "ua_detrac"], index=0)
        if model_choice == "vis_drone":
            model_path = r"C:\Users\NITRO 5\Desktop\All_JUP\visDrone\best (2).pt"
        else:
            model_path = r"C:\Users\NITRO 5\Downloads\best (3).pt"
    try:
        model = helper.load_model(model_path)
    except Exception as ex:
        st.error(f"Unable to load model. Check the specified path: {model_path}")
        st.error(ex)
    source_img = None
    # If image is selected
    if source_radio == settings.IMAGE:
        with col1:
            source_img = st.file_uploader(
                "Choose an image...", type=("jpg", "jpeg", "png", "bmp", "webp")
            )
        with col2:
            try:
                if source_img is not None:
                    uploaded_image = PIL.Image.open(source_img)

                    st.image(
                        source_img, caption="Uploaded Image", use_column_width=True
                    )
            except Exception as ex:
                st.error("Error occurred while opening the image.")
                st.error(ex)

        with col1:
            if source_img is not None:
                if st.button("Detect Objects"):
                    helper.image_handler(
                        model_choice, model, uploaded_image, confidence, col2, col3
                    )

    elif source_radio == settings.VIDEO:
        helper.play_stored_video(confidence, model_path, col1, col2, col3)

    elif source_radio == settings.YOUTUBE:
        helper.play_youtube_video(confidence, model_path, col3)

    else:
        st.error("Please select a valid source type!")
else:
    st.title("you are not allowed to enter")
